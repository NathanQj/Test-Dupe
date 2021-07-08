# -*- coding: utf-8 -*-
import base64
from io import BytesIO
import xlsxwriter
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class link_tracker(models.Model):
    _inherit = "link.tracker"

    @api.multi
    def print_excel_report(self):
        # Method to print sale order open order excel report
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        title_format = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'align': 'center'})
        header_format = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 12, 'bold': 1,
             'align': 'center'})
        header_format.set_text_wrap()
        row_header_format = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'bold': 1,
             'align': 'center'})
        align_right = workbook.add_format(
            {'align': 'right', 'font_size': 10})
        row_format = workbook.add_format(
            {'font_size': 10})
        row_format.set_text_wrap()

        worksheet = workbook.add_worksheet('New Donor Aquisition')
        current_year = str(datetime.now().year)
        worksheet.write(
            0, 0, 'Year: ' + current_year, title_format)

        worksheet.set_column('A:A', 30)

        row = 3
        col = 0

        worksheet.write(row, col, 'Ad Spend', row_format)
        worksheet.set_row(row + 1, 28)
        worksheet.write(row + 1, col, 'Registered: Completed Page 1 of Registration Form', row_format)
        worksheet.write(row + 2, col, 'Scheduled: Completed Online Registration', row_format)
        worksheet.write(row + 3, col, 'Visit: Visit Started at B Positive Plasma', row_format)
        worksheet.write(row + 4, col, 'Complete Screening', row_format)
        worksheet.write(row + 5, col, 'Complete Physical', row_format)
        worksheet.write(row + 6, col, 'Complete Donation', row_format)
        worksheet.set_row(row + 7, 28)
        worksheet.write(row + 7, col, 'Approved Donor : 2 donations and lab results', row_format)
        worksheet.write(row + 8, col, 'Cost to Acquire a Donor (CAD)', row_format)

        row = 1
        col = 1
        worksheet.write(row, col, '#')
        worksheet.write(row, col+2, '%')

        row = 2
        col = 1
        worksheet.merge_range(
            row, col, row, col+2, 'January')

        col = 4
        for month in range(2,13):
            worksheet.write(1, col, '#')
            worksheet.write(1, col + 1, '%')
            worksheet.merge_range(
               row, col, row, col+1, calendar.month_name[month])
            col += 2

        workbook.close()
        fp.seek(0)
        result = base64.b64encode(fp.read())
        attachment_obj = self.env['ir.attachment']
        filename = 'New Donor Aquisition'

        attachment_id = attachment_obj.create(
            {'name': filename,
             'datas_fname': filename,
             'datas': result})

        download_url = 'web/content/' + \
                       str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
            'nodestroy': False,
        }
    # else:
    #     raise UserError(_('No records found'))