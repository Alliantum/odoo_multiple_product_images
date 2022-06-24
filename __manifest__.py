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
    'version': '14.0.1.1.1',
    'depends': ['product', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'data/clean_orphans_images.xml',
        'views/assets.xml',
        'views/product_image_backend.xml',

    ]
}
