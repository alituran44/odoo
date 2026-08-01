{
    'name': 'Google Ads & Meta Ads Reklam Paneli',
    'version': '17.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Google Ads ve Meta Ads (Facebook & Instagram) Harcama ve Performans Paneli',
    'description': """
Ajanslar İçin Google Ads ve Meta Ads Harcama ve Dönüşüm Takip Paneli.
- Google Ads ve Meta Ads hesap tanımlamaları
- Kampanya bazlı harcama (Spend), Tıklama (CPC), Gösterim (Impressions) ve Dönüşüm (CPA/ROAS) takibi
- Müşteri firmalara göre reklam bütçesi raporlaması
    """,
    'author': 'Antigravity Agency Team',
    'website': 'https://www.odoo.com',
    'depends': ['base', 'mail', 'crm', 'utm'],
    'data': [
        'security/ir.model.access.csv',
        'views/ads_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
