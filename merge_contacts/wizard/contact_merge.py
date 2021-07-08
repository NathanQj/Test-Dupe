# -*- coding: utf-8 -*-

from ast import literal_eval
import functools
import itertools
import logging
import psycopg2
import inspect

from odoo import api, fields, models
from odoo import SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import mute_logger

_logger = logging.getLogger('base.partner.merge')

class ContactMerge(models.TransientModel):

    _inherit = 'base.partner.merge.automatic.wizard'

    # Group by
    group_by_x_studio_first_name = fields.Boolean('First Name')
    group_by_x_studio_last_name = fields.Boolean('Last Name')
    group_by_x_donation_number = fields.Boolean('Donor Number')



    @api.multi
    def _process_query(self, query):
        """ Execute the select request and write the result in this wizard
            :param query : the SQL query used to fill the wizard line
        """
        self.ensure_one()
        model_mapping = self._compute_models()

        # group partner query
        self._cr.execute(query)

        counter = 0
        for min_id, aggr_ids in self._cr.fetchall():

            # To ensure that the used partners are accessible by the user
            partners = self.env['res.partner'].search([('id', 'in', aggr_ids)])
            _logger.info('min_id: ' + str(min_id))
            _logger.info('aggr_ids: ' + str(aggr_ids))
            if len(partners) < 2:
                continue

            # exclude partner according to options
            if model_mapping and self._partner_use_in(partners.ids, model_mapping):
                continue
            #Filter the list of contact by excluding partner that use one of the tags

            if self.x_studio_tag_settings:
                _logger.info('Tag Setting: ' + str(self.x_studio_tag_settings) + ' for tags = ' + str(self.x_studio_excluded_tags.ids))
                partners_filtered = []
                for partner in partners:
                    #Search on each tag it the tag match one of the tag
                    if self.x_studio_tag_settings == 'Excluded':
                        #is disjoint = don't share one item
                        toInclude = set(list(partner.category_id.ids)).isdisjoint(self.x_studio_excluded_tags.ids)
                        _logger.info('Partner: ' + str(partner.id) + ' is toInclude = ' + str(toInclude) + ' with partner.category_id = ' + str(set(list(partner.category_id.ids))))

                        # for tag in partner['category_id']:
                        #     if tag.id in self.x_studio_excluded_tags.ids:
                        #         toExclude = True
                        #     else:
                        #         toExclude = False
                        #         continue
                        if toInclude == True:
                            partners_filtered.append(partner.id)
                            counter += 1

                    elif self.x_studio_tag_settings == 'Included':
                        #is disjoint = don't share any items
                        toInclude = not set(list(partner.category_id.ids)).isdisjoint(self.x_studio_included_tags.ids)
                        _logger.info('Partner: ' + str(partner.id) + ' should be toInclude = ' + str(toInclude) + ' with partner.category_id = ' + str(set(list(partner.category_id.ids))))

                        # for tag in partner['category_id']:
                        #     if tag.id in self.x_studio_included_tags.ids:
                        #         toExclude = False
                        #     else:
                        #         toExclude = True
                        #         continue
                        if toInclude == True:
                            partners_filtered.append(partner.id)
                            counter += 1

                if len(partners_filtered) < 2:
                    continue

                _logger.info('partners filtered: ' + str(partners_filtered))


                self.env['base.partner.merge.line'].create({
                    'wizard_id': self.id,
                    'min_id': min_id,
                    'aggr_ids': partners_filtered
                })
                counter += 1
            else:
                self.env['base.partner.merge.line'].create({
                    'wizard_id': self.id,
                    'min_id': min_id,
                    'aggr_ids': partners.ids,
                })
                counter += 1

        self.write({
            'state': 'selection',
            'number_group': counter,
        })

        _logger.info("counter: %s", counter)


    @api.model
    def _generate_query(self, fields, maximum_group=100):
        """ Build the SQL query on res.partner table to group them according to given criteria
            :param fields : list of column names to group by the partners
            :param maximum_group : limit of the query
        """
        # make the list of column to group by in sql query
        sql_fields = []
        #_logger.info('Fields: ' + str(fields))
        for field in fields:
            if field in ['email', 'name']:
                sql_fields.append('lower(%s)' % field)
            elif field in ['vat']:
                sql_fields.append("replace(%s, ' ', '')" % field)
            else:
                sql_fields.append(field)
        group_fields = ', '.join(sql_fields)

        # where clause : for given group by columns, only keep the 'not null' record
        filters = []
        for field in fields:
            if field in ['email', 'name', 'vat', 'x_studio_first_name', 'x_studio_last_name', 'x_donation_number']:
                filters.append((field, 'IS NOT', 'NULL'))

        criteria = ' AND '.join('%s %s %s' % (field, operator, value) for field, operator, value in filters)

        # build the query
        text = [
            "SELECT min(id), array_agg(id)",
            "FROM res_partner",
        ]

        if criteria:
            text.append('WHERE %s' % criteria)

        text.extend([
            "GROUP BY %s" % group_fields,
            "HAVING COUNT(*) >= 2",
            "ORDER BY min(id)",
        ])

        if maximum_group:
            text.append("LIMIT %s" % maximum_group,)

        return ' '.join(text)


    @api.model
    def _merge(self, partner_ids, dst_partner=None):
        """ private implementation of merge partner
            :param partner_ids : ids of partner to merge
            :param dst_partner : record of destination res.partner
        """
        Partner = self.env['res.partner']
        partner_ids = Partner.browse(partner_ids).exists()
        if len(partner_ids) < 2:
            return

        #if len(partner_ids) > 3:
            #_logger.info('More than 3!')
        #    raise UserError(_("For safety reasons, you cannot merge more than 3 contacts together. You can re-open the wizard several times if needed."))

        # check if the list of partners to merge contains child/parent relation
        child_ids = self.env['res.partner']
        for partner_id in partner_ids:
            child_ids |= Partner.search([('id', 'child_of', [partner_id.id])]) - partner_id
        if partner_ids & child_ids:
            raise UserError(_("You cannot merge a contact with one of his parent."))

        # check only admin can merge partners with different emails
        #if SUPERUSER_ID != self.env.uid and len(set(partner.email for partner in partner_ids)) > 1:
        #    raise UserError(_("All contacts must have the same email. Only the Administrator can merge contacts with different emails."))

        # remove dst_partner from partners to merge
        if dst_partner and dst_partner in partner_ids:
            src_partners = partner_ids - dst_partner
        else:
            ordered_partners = self._get_ordered_partner(partner_ids.ids)
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]
        _logger.info("dst_partner: %s", dst_partner.id)

        # From Odoo source: FIXME: is it still required to make and exception for account.move.line since accounting v9.0 ?
        if SUPERUSER_ID != self.env.uid and 'account.move.line' in self.env and self.env['account.move.line'].sudo().search([('partner_id', 'in', [partner.id for partner in src_partners])]):
            raise UserError(_("Only the destination contact may be linked to existing Journal Items. Please ask the Administrator if you need to merge several contacts linked to existing Journal Items."))

        # call sub methods to do the merge
        self._update_foreign_keys(src_partners, dst_partner)
        self._update_reference_fields(src_partners, dst_partner)
        self._update_values(src_partners, dst_partner)

        _logger.info('(uid = %s) merged the partners %r with %s', self._uid, src_partners.ids, dst_partner.id)
        dst_partner.message_post(body='%s %s' % (_("Merged with the following partners:"), ", ".join('%s <%s> (ID %s)' % (p.name, p.email or 'n/a', p.id) for p in src_partners)))

        # delete source partner, since they are merged
        src_partners.unlink()
