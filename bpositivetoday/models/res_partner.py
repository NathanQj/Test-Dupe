from lxml import etree

from odoo import models, api

EDITABLE_FIELDS = {
    'center_role': ['category_id', 'x_donation_number', 'comment'],
    'corporate_role': []
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Makes fields readonly depending on user groups"""
        res = super(ResPartner, self)._fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        user = self.env.user
        if not user._is_admin():
            editable_fields = user.has_group('bpositivetoday.group_center_role') and EDITABLE_FIELDS.get(
                'center_role') or user.has_group('bpositivetoday.group_corporate_role') and EDITABLE_FIELDS.get(
                'corporate_role')
            if view_type == 'form' and editable_fields is not None:
                doc = etree.XML(res['arch'])
                method_nodes = doc.xpath("//field")
                for node in method_nodes:
                    if node.get('name', False) and node.get('name', False) not in editable_fields:
                        node.set('readonly', "1")
                res['arch'] = etree.tostring(doc)
        return res
