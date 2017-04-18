# -*- coding: utf-8 -*-

##############################################################################
#
#    Clear Groups for Odoo
#    Copyright (C) 2016 Bytebrand GmbH (<http://www.bytebrand.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from datetime import date, timedelta
from openerp import models, fields, api



class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def getDuration(self, payslip):
        duration = 0.0

        user_id =  self.user_id.id

        tsheet_obj = self.env['account.analytic.line']

        timesheets = tsheet_obj.search([('user_id', '=', user_id), ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to),('account_id', '=', 2 ) ])
        #timesheets = tsheet_obj.search([('user_id', '=', payslip.user_id),   ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to)])
        for tsheet in timesheets: #counting duration from timesheets
            duration += tsheet.unit_amount
        return duration




class hr_account_analine(models.Model):
    _inherit = 'account.analytic.line'

    attn_type = fields.Char()
    in_dt = fields.Datetime()
    out_dt = fields.Datetime()
    employee_id = fields.Integer()


