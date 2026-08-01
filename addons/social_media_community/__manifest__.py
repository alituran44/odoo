{
    'name': 'Sosyal Medya Yönetimi (Topluluk Sürümü)',
    'version': '1.0',
    'category': 'Marketing',
    'summary': 'Sosyal Medya hesapları, içerik takvimi, gönderi zamanlama ve müşteri onay yönetimi.',
    'author': 'Antigravity',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/social_post_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
