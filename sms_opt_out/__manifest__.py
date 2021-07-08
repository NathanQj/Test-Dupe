# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "SMS Opt-Out",
  "summary"              :  """""",
  "category"             :  "Marketing",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=sms_opt_out&version=12.0",
  "depends"              :  [
                             'sms_notification',
                             'website',
                            ],
  "data"                 :  [
                             'edi/sms_templates_data.xml',
                             'views/res_config_settings_view.xml',
                             'views/sms_template_view.xml',
                             'views/res_partner_view.xml',
                             'views/website_templates.xml',
                            ],
  "demo"                 :  [],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  36,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}