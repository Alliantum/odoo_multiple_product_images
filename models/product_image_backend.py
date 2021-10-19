# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.image import image_get_resized_images
import logging
import base64

_logger = logging.getLogger(__name__)



# Here we declare de model of a category which will be a field of the image class later
class ProductImageCategory(models.Model):
    _name = 'product.image.category'
    _description = "An image category"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    images_ids = fields.Many2many('product.image.backend', string="Images")
    color = fields.Integer('Color')
    images_counter = fields.Integer('Images Count', compute="_get_counters")
    products_tmpl_counter = fields.Integer('Template Count', compute="_get_counters")
    products_counter = fields.Integer('Products Count', compute="_get_counters")

    def _get_counters(self):
        for categ in self:
            templates_ids = []
            product_ids = []
            for image_id in categ.images_ids:
                if image_id.template_id:
                    templates_ids.append(image_id.template_id.id)
                elif image_id.product_id:
                    product_ids.append(image_id.product_id.id)
            categ.products_tmpl_counter = len(templates_ids)
            categ.products_counter = len(product_ids)
            categ.images_counter = len(categ.images_ids)

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        for category in self:
            other_id = self.search([('id', '!=', category.id), ('name', '=', category.name)], limit=1)
            if other_id:
                raise ValidationError(
                    _("This category name is already in use."))

    def show_images_category(self):
        if self.images_ids:
            action = {
                'type': 'ir.actions.act_window',
                'name': _('Images by Category'),
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'product.image.backend',
                'domain': [('id', 'in', self.images_ids.ids)]
            }
            return action
        return

    @api.multi
    def show_products_category(self):
        self.ensure_one()
        if self.images_ids:
            product_ids = [image_id.product_id.id for image_id in self.images_ids if image_id.product_id]
            action = {
                'type': 'ir.actions.act_window',
                'name': _('Products by Category'),
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'product.product',
                'domain': [('id', 'in', product_ids)]
            }
            return action
        return

    @api.multi
    def show_templates_category(self):
        self.ensure_one()
        if self.images_ids:
            template_ids = [image_id.template_id.id for image_id in self.images_ids if image_id.template_id]
            action = {
                'type': 'ir.actions.act_window',
                'name': _('Products by Category'),
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'res_model': 'product.template',
                'domain': [('id', 'in', template_ids)]
            }
            return action
        return

# This will be de model of every image in the database
class ProductImageBackend(models.Model):
    _name = 'product.image.backend'
    _description = 'Product Image Backend'

    name = fields.Char('Name', required=True)
    image = fields.Image('Image', attachment=True)
    image_medium = fields.Image(
        "Medium-sized image",
        related='image',
        max_width=386,
        max_height=386,
        store=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Image(
        "Small-sized image",
        related='image',
        max_width=128,
        max_height=128,
        store=True,
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    raw_image_size = fields.Integer(compute="_compute_raw_image_size")
    filename = fields.Char()
    product_id = fields.Many2one('product.product', 'Related Product', copy=True)
    template_id = fields.Many2one('product.template', 'Related Template', copy=True)
    category_ids = fields.Many2many('product.image.category', string="Categories")
    trigger = fields.Boolean('Trigger', compute="get_trigger")
    origin_id = fields.Integer('Origin')

    @api.depends('image')
    def _compute_raw_image_size(self):
        for backend_image in self:
            if backend_image.image:
                # In Kb
                backend_image.raw_image_size = len(base64.b64decode(backend_image.image)) // 1000

    # This method pretains to trigger and its just used as a lifecycle method, to get always trigger when the model is loaded.
    @api.multi
    def get_trigger(self):
        if self.env.context.get('default_origin'):
            for image in self:
                if image.id:
                    query = """UPDATE product_image_backend SET origin_id = %s WHERE id = %s;"""
                    params = (self.env.context.get('default_origin'), image.id)
                    self.env.cr.execute(query, params)

    # This method gives the ability to switch an image between the actual product or the template
    @api.multi
    def switch_image(self):
        self.ensure_one()
        if self.env.context.get('switch') and self.env.context['switch'] == 'to_template':
            self.template_id = self.product_id.product_tmpl_id
            self.product_id = ''
            return {
                'type': 'ir.actions.act_view_reload',
            }
        elif self.env.context.get('switch') and self.env.context['switch'] == 'to_variant':
            variant_id = self.env['product.product'].browse(self.origin_id)
            self.product_id = variant_id
            self.template_id = ''
            return {
                'type': 'ir.actions.act_view_reload'
            }
        pass

    # This is just a trash collector, then delete it
    @api.model
    def clean_orphans_images(self):
        all_orphans_images = self.search([('template_id', '=', False), ('product_id', '=', False)])
        if all_orphans_images:
            all_orphans_images.unlink()

# And finally we embed our new model onto product and his template classes
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_image_backend_ids = fields.One2many('product.image.backend', 'template_id')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_image_backend_ids = fields.One2many('product.image.backend', 'product_id', string='Images')
    related_template_image_backend_ids = fields.One2many('product.image.backend', compute="_get_template_images", inverse="_set_template_image", string="Template Images")

    def _get_template_images(self):
        for product in self:
            product.related_template_image_backend_ids = product.product_tmpl_id.template_image_backend_ids

    def _set_template_image(self):
        self.product_tmpl_id.template_image_backend_ids = self.related_template_image_backend_ids
