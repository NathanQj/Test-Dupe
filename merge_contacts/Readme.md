
# Merge Contact Wizard

Hi! I'm your first Markdown file in **StackEdit**. If you want to learn about StackEdit, you can read me. If you want to play with Markdown, you can edit me. Once you have finished with me, you can create new files by opening the **file explorer** on the left corner of the navigation bar.


---

 1. [Overview](#Overview)
	 1. [Why does this tool exist?](#Why-does-this-tool-exist?)
	 2. [Functional Structure](#functional-structure)
	 3. [History](#history)
 2. [Setup Procedure](#setup)
	 4. [Compatibility](#compatibility)
	 5. [Installation Guide](#installation-guide)
 3. [User Guide](#user-guide)
 4. [Controllers](#Controllers)
 5. [Appendix](#Appendix)
    1. [Mermaids](#mermaids-overview)
       1. [Overview](#overview)

---

## Overview

### Why does this tool exist?
Due to the lack of formal account system, it is often the case that Bpositive's donors get registered in Odoo's contact module more than once. This creates issues when with regard to connecting said donors to  the CRM and Donation Models, which makes both tracking their donations to the Contact impossible, and sullies the quality of Marketing data (see the Donor Acquisition Report for more detail). 

This module seeks to alleviate, if not outright eliminate these woes by offering a post hoc method of deleting excess contact records while adding any additional information they may hold back to the original contact (the earliest created record).

### Functional Structure
<!-- Given that this module takes the same code scaffolding as all standard Odoo modules this document shall forgo any need for explanation of it and rather focus on what fuctions the module currently provides. -->
This module eschews the traditional MVC framework in favor of a controller only approach. Which this may not appear to be true upon first glance, upon investigation, the *models*, *views*, & *controllers* folders contain nothing but commented code. 

The real "meat" of the module is all contained withing the *wizard* folder, titled *contact_merge.py*. This works because the module, is fundamentally nothing more then an extension of the base module:

`base.partner.merge.automatic.wizard`
### History
This module is stored and revised through Bpositives Github. 
[https://github.com/215marketing/bpositivetoday/tree/master/merge_contacts](https://github.com/215marketing/bpositivetoday/tree/master/merge_contacts)

---
## Setup Procedure
### Compatibility

### Installation Guide

## Controller

### Function 1: 

Execute the select request and write the result in this wizard.     
		`def _process_query(self, query):`     
*param*: **query** : The SQL query used to fill the wizard line.

`for min_id, aggr_ids in self._cr.fetchall():`
            
To ensure that the used partners are accessible by the user:    
`partners = self.env['res.partner'].search([('id', 'in',aggr_ids)])`

To ensure that contacts with less that 2 records are excluded:
`if len(partners) < 2: continue`




#### Filtering by tag

 To enable that users can filter based on *`category_ids`* that they'd like to **exclude** or **include**, the filtering statement was written as if, elif statement. 
 
 :beetle: <span style="color:red"> **Known Issue #34:** 
 [Merge Duplicates- "tuple out of range"](https://github.com/215marketing/bpositivetoday/issues/34)

Exclude partner according to options
Filter the list of contact by excluding partner that use one of the tags

            if model_mapping and self._partner_use_in(partners.ids, model_mapping):
                continue

Search on each tag it the tag match one of the tag:


            partners_filtered = []
            for partner in partners:
                if self.x_studio_tag_settings == 'Excluded':
                    toExclude = False
                    for tag in partner['category_id']:
                        if tag.id in self.x_studio_excluded_tags.ids:
                            toExclude = True     
                        else:
                            toExclude = False                                 
                    if toExclude == False:
                        partners_filtered.append(partner.id)
                        counter += 1 
                elif self.x_studio_tag_settings == 'Included':         
                    #toExclude = True
                    for tag in partner['category_id']:
                        if tag.id in self.x_studio_included_tags.ids:
                            toExclude = False   
                        else:
                            toExclude = True                               
                    if toExclude == False:
                        partners_filtered.append(partner.id)
                        counter += 1

                if len(partners_filtered) < 2:
                    continue
					            self.env['base.partner.merge.line'].create({
                'wizard_id': self.id,
                'min_id': min_id,
                'aggr_ids': partners_filtered
            })

        self.write({
            'state': 'selection',
            'number_group': counter,
        })

### Function 2: 
		def _generate_query(self, fields, maximum_group=100):


Build the SQL query on res.partner table to group them according to given criteria
            :param fields : list of column names to group by the partners
            :param maximum_group : limit of the query
		
make the list of column to group by in sql query
        
		sql_fields = []
        for field in fields:
            if field in ['email', 'name']:
                sql_fields.append('lower(%s)' % field)
            elif field in ['vat']:
                sql_fields.append("replace(%s, ' ', '')" % field)
            else:
                sql_fields.append(field)
        group_fields = ', '.join(sql_fields)

where clause : for given group by columns, 
only keep the 'not null' record
        
		filters = []
        for field in fields:
            if field in ['email', 'name', 'vat', 'x_studio_first_name', 'x_studio_last_name', 'x_donation_number']:
                filters.append((field, 'IS NOT', 'NULL'))
				...
Build the query:

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

### Function 3:
private implementation of merge partner   
param partner_ids : ids of partner to merge   
param dst_partner : record of destination res.partner

		def _merge(self, partner_ids, dst_partner=None):
     		Partner = self.env['res.partner']
        	partner_ids = Partner.browse(partner_ids).exists()
        	if len(partner_ids) < 2:
            	return

Check if the list of partners to merge contains child/parent relation

		child_ids = self.env['res.partner']
			for partner_id in partner_ids:
				child_ids |= Partner.search([('id', 'child_of', [partner_id.id])]) - partner_id
			if partner_ids & child_ids:
				raise UserError(_("You cannot merge a contact with one of his parent."))

Remove dst_partner from partners to merge:

        if dst_partner and dst_partner in partner_ids:
            src_partners = partner_ids - dst_partner
        else:
            ordered_partners = self._get_ordered_partner(partner_ids.ids)
            dst_partner = ordered_partners[-1]
            src_partners = ordered_partners[:-1]
[![](https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcblx0QVtGT1IgZmllbGQgeF0gLS0-fHJlY29yZF9hLmZpZWxkX3ggPSByZWNvcmRfYi5maWVsZF94fEMoRm9yIHJlY29yZF8uLi4pXG5cdEMgLS0-fGluZGV4PSAtMXwgRFtkc3QgcGFydG5lciA9IGxhc3QgaW4gbGlzdF1cblx0QyAtLT58c2xpY2UgPSAtMXwgRVtzcmMgcGFydG5lciA9IHJlY29yZHMgIT0gZHN0IHBhcnRuZXJdXG5cblx0XHRcdFx0XHQiLCJtZXJtYWlkIjp7InRoZW1lIjoiZGVmYXVsdCJ9LCJ1cGRhdGVFZGl0b3IiOmZhbHNlfQ)](https://mermaid-js.github.io/mermaid-live-editor/#/edit/eyJjb2RlIjoiZ3JhcGggVERcblx0QVtGT1IgZmllbGQgeF0gLS0-fHJlY29yZF9hLmZpZWxkX3ggPSByZWNvcmRfYi5maWVsZF94fEMoRm9yIHJlY29yZF8uLi4pXG5cdEMgLS0-fGluZGV4PSAtMXwgRFtkc3QgcGFydG5lciA9IGxhc3QgaW4gbGlzdF1cblx0QyAtLT58c2xpY2UgPSAtMXwgRVtzcmMgcGFydG5lciA9IHJlY29yZHMgIT0gZHN0IHBhcnRuZXJdXG5cblx0XHRcdFx0XHQiLCJtZXJtYWlkIjp7InRoZW1lIjoiZGVmYXVsdCJ9LCJ1cGRhdGVFZGl0b3IiOmZhbHNlfQ)

*Chart 3.1: The seperation of records prior to merging.*

:beetle: **From Odoo Source:** 
<span style="color:red"> 
FIXME: is it still required to make and exception for account.move.line since accounting v9.0 ? </span>

        if SUPERUSER_ID != self.env.uid and 'account.move.line' in self.env and self.env['account.move.line'].sudo().search([('partner_id', 'in', [partner.id for partner in src_partners])]):
            raise UserError(_("Only the destination contact may be linked to existing Journal Items. Please ask the Administrator if you need to merge several contacts linked to existing Journal Items."))

call sub methods to do the merge

        self._update_foreign_keys(src_partners, dst_partner)
        self._update_reference_fields(src_partners, dst_partner)
        self._update_values(src_partners, dst_partner)

delete source partner, since they are merged

        src_partners.unlink()

## User Guide

## Appendix 
### Mermaids
#### Overview


