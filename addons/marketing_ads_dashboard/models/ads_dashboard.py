from odoo import models, fields, api, _

class AdsAccount(models.Model):
    _name = 'ads.account'
    _description = 'Reklam Hesabı (Google & Meta)'
    _inherit = ['mail.thread']

    name = fields.Char(string='Reklam Hesabı Adı', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Müşteri / Firma', required=True, tracking=True)
    provider = fields.Selection([
        ('google', 'Google Ads'),
        ('meta', 'Meta Ads (Facebook & Instagram)'),
        ('tiktok', 'TikTok Ads'),
        ('linkedin', 'LinkedIn Ads')
    ], string='Reklam Platformu', required=True, default='google', tracking=True)
    account_id = fields.Char(string='Reklam Hesap ID', required=True, help='Örn: act_123456789 veya Google CID: 123-456-7890')
    currency_id = fields.Many2one('res.currency', string='Para Birimi', default=lambda self: self.env.company.currency_id)
    
    daily_budget = fields.Monetary(string='Günlük Bütçe', currency_field='currency_id', tracking=True)
    total_spend = fields.Monetary(string='Toplam Harcanan Tutar (₺)', currency_field='currency_id', compute='_compute_metrics', store=True)
    total_clicks = fields.Integer(string='Toplam Tıklanma', compute='_compute_metrics', store=True)
    total_impressions = fields.Integer(string='Toplam Gösterim', compute='_compute_metrics', store=True)
    conversions = fields.Integer(string='Dönüşüm Sayısı (Lead/Satış)', compute='_compute_metrics', store=True)
    cpc = fields.Float(string='Ortalama Tıklama Maliyeti (CPC ₺)', compute='_compute_metrics', store=True)
    cpa = fields.Float(string='Dönüşüm Başı Maliyet (CPA ₺)', compute='_compute_metrics', store=True)
    roas = fields.Float(string='Ortalama ROAS (Getiri Oranı x)', compute='_compute_metrics', store=True)

    campaign_ids = fields.One2many('ads.campaign', 'ads_account_id', string='Reklam Kampanyaları')
    active = fields.Boolean(default=True)

    @api.depends('campaign_ids.spend', 'campaign_ids.clicks', 'campaign_ids.impressions', 'campaign_ids.conversions', 'campaign_ids.roas')
    def _compute_metrics(self):
        for acc in self:
            spend = sum(acc.campaign_ids.mapped('spend'))
            clicks = sum(acc.campaign_ids.mapped('clicks'))
            impressions = sum(acc.campaign_ids.mapped('impressions'))
            conversions = sum(acc.campaign_ids.mapped('conversions'))
            
            acc.total_spend = spend
            acc.total_clicks = clicks
            acc.total_impressions = impressions
            acc.conversions = conversions
            acc.cpc = round(spend / clicks, 2) if clicks > 0 else 0.0
            acc.cpa = round(spend / conversions, 2) if conversions > 0 else 0.0
            roas_list = [c.roas for c in acc.campaign_ids if c.roas > 0]
            acc.roas = round(sum(roas_list) / len(roas_list), 2) if roas_list else 0.0


class AdsCampaign(models.Model):
    _name = 'ads.campaign'
    _description = 'Reklam Kampanyası'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, id desc'

    name = fields.Char(string='Kampanya Adı', required=True, tracking=True)
    ads_account_id = fields.Many2one('ads.account', string='Reklam Hesabı', required=True, ondelete='cascade', tracking=True)
    partner_id = fields.Many2one('res.partner', related='ads_account_id.partner_id', string='Müşteri Firma', store=True, readonly=True)
    provider = fields.Selection(related='ads_account_id.provider', string='Platform', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='ads_account_id.currency_id', string='Para Birimi', readonly=True)
    
    status = fields.Selection([
        ('active', '🟢 Yayında / Aktif'),
        ('paused', '🟡 Duraklatıldı'),
        ('completed', '🔵 Tamamlandı')
    ], string='Kampanya Durumu', default='active', required=True, tracking=True)
    
    budget = fields.Monetary(string='Kampanya Bütçesi', currency_field='currency_id', tracking=True)
    spend = fields.Monetary(string='Harcanan Tutar (₺)', currency_field='currency_id', tracking=True)
    impressions = fields.Integer(string='Gösterim Sayısı', tracking=True)
    clicks = fields.Integer(string='Tıklama Sayısı', tracking=True)
    ctr = fields.Float(string='Tıklanma Oranı (CTR %)', compute='_compute_ctr', store=True)
    cpc = fields.Float(string='Tıklama Başı Maliyet (CPC ₺)', compute='_compute_cpc', store=True)
    conversions = fields.Integer(string='Dönüşüm Sayısı (Lead)', tracking=True)
    cpa = fields.Float(string='Dönüşüm Başı Maliyet (CPA ₺)', compute='_compute_cpa', store=True)
    roas = fields.Float(string='ROAS (Getiri Katı x)', default=1.0, tracking=True)
    
    start_date = fields.Date(string='Başlangıç Tarihi', default=fields.Date.today)
    end_date = fields.Date(string='Bitiş Tarihi')
    notes = fields.Text(string='Kampanya Notları & Hedefleme Detayları')

    @api.depends('clicks', 'impressions')
    def _compute_ctr(self):
        for camp in self:
            camp.ctr = round((camp.clicks / camp.impressions) * 100, 2) if camp.impressions > 0 else 0.0

    @api.depends('spend', 'clicks')
    def _compute_cpc(self):
        for camp in self:
            camp.cpc = round(camp.spend / camp.clicks, 2) if camp.clicks > 0 else 0.0

    @api.depends('spend', 'conversions')
    def _compute_cpa(self):
        for camp in self:
            camp.cpa = round(camp.spend / camp.conversions, 2) if camp.conversions > 0 else 0.0
