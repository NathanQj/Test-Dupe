from lxml import etree

from odoo import models, api

EDITABLE_FIELDS = {
    'center_role': ['stage_id'],
    'corporate_role': []
}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Make all fields in the form view readonly for users under Center Role"""
        res = super(CrmLead, self)._fields_view_get(
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
            if editable_fields is not None:
                doc = etree.XML(res['arch'])
                method_nodes = doc.xpath("//field")
                for node in method_nodes:
                    if node.get('name', False) and node.get('name', False) not in editable_fields:
                        node.set('readonly', "1")
                res['arch'] = etree.tostring(doc)
        return res
