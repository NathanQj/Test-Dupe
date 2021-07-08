from odoo import models, api, tools

CENTER_ROLE_GROUP = 'bpositivetoday.group_center_role'
CORPORATE_ROLE_GROUP = 'bpositivetoday.group_corporate_role'


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        """Inherited to change the visible menu ids of Corporate and Center role users"""
        res = super(IrUiMenu, self)._visible_menu_ids(debug=debug)
        user = self.env.user
        if not user._is_admin():
            is_center_role = user.has_group(CENTER_ROLE_GROUP)
            is_corporate_role = user.has_group(CORPORATE_ROLE_GROUP)
            group_id = is_center_role and self.env.ref(CENTER_ROLE_GROUP) or is_corporate_role and self.env.ref(
                CORPORATE_ROLE_GROUP)
            if group_id:
                menu_ids = self.browse(res)
                menus = menu_ids.filtered(lambda menu: group_id & menu.groups_id)
                for menu in menu_ids:
                    parent_menu = menu.parent_id
                    while menu and parent_menu in menus and menu not in menus:
                        menus |= menu
                        menu = menu.parent_id
                return menus.ids
        return res
