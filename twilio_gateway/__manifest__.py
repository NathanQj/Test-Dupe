# -*- coding: utf-8 -*-
##########################################################################
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
##########################################################################
{
  "name"                 :  "Twilio SMS Gateway",
  "summary"              :  """Send text messages with Twilio in Odoo. The module allows the Odoo user to use Twilio to send SMS to customers.""",
  "category"             :  "Marketing",
  "version"              :  "1.2.2",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-SMS-Twilio-Gateway.html",
  "description"          :  """Twilio communication
Odoo Twilio SMS Gateway
Use Twilio in odoo
Twilio communication
Bulk SMS send
Send Bulk SMS
Twilio odoo
Twilio SMS alert
Integrate SMS Gateways with Odoo
Odoo SMS Notification
Send Text Messages to mobile
Integrate SMS Gateways with Odoo
SMS Gateway
SMS Notification
Notify with Odoo SMS 
Mobile message send
Send Mobile messages
Mobile notifications to customers
Mobile Notifications to Users
How to get SMS notification in Odoo
module to get SMS notification in Odoo
SMS Notification app in Odoo
Notify SMS in Odoo
Add SMS notification feature to your Odoo
Mobile SMS feature
How Odoo can help to get SMS notification,
Odoo SMS OTP Authentication,
Marketplace SMS
Plivo SMS Gateway
Clicksend SMS Gateway
Skebby SMS Gateway
Mobily SMS Gateway
MSG91 SMS Gateway
Netelip SMS Gateway""",
  "live_test_url"        :  "https://webkul.com/blog/odoo-sms-twilio-gateway/",
  "depends"              :  ['sms_notification'],
  "data"                 :  [
                             'views/twilio_config_view.xml',
                             'views/sms_report.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  50,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "external_dependencies":  {'python': ['twilio', 'urllib3']},
}
