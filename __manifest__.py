# -*- coding: utf-8 -*-
{
    'name': "os_alveus_multiple_images",
    'summary': """
        Multiple Images on Products""",
    'description': """
        
    """,
    'author': "Open Solutions",
    'website': "",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['product', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_image_backend.xml',
        'views/assets.xml',
        'data/clean_orphans_images.xml',
    ]
}