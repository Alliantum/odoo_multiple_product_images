# -*- coding: utf-8 -*-
{
    'name': "Multiple Images",
    'summary': """
        Multiple Images and Categories on Products""",
    'description': """
        Creates an image gallery section available on every product and also on the product templates.
    """,
    'author': "Alliantum",
    'website': "https://www.alliantum.com/",
    'category': 'Inventory',
    'license': 'AGPL-3',
    'version': '13.0.1.0.1',
    'depends': ['product', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_image_backend.xml',
        'views/assets.xml',
        'data/clean_orphans_images.xml',
    ]
}
