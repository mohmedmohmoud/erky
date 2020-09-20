from odoo import models, fields, api

FONTS_FAMILY = [('serif', "Serif"),
                ('cursive', "Sursive"),
                ('emoji', "Emoji")]

FONT_STYLE = [('normal', 'Normal'),
              ('italic', 'Italic'),
              ('oblique', 'Oblique')]

class DynamicTemplateReport(models.Model):
    _name = "erky.dynamic.template"

    name = fields.Char("Template Name", required=1)
    dyn_template_line_ids = fields.One2many("erky.dynamic.template.line", "dynamic_template_id")


class DynamicTemplateLines(models.Model):
    _name = "erky.dynamic.template.line"

    dynamic_template_id = fields.Many2one("erky.dynamic.template")
    temp_body = fields.Html("Template Text")
    rep_style = fields.Text("Style", required=1)
