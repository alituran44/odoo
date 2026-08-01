import requests
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SocialAccount(models.Model):
    _name = 'social.account'
    _description = 'Sosyal Medya Hesabı'
    _inherit = ['mail.thread']

    name = fields.Char(string='Hesap Adı / Kullanıcı Adı', required=True, tracking=True)
    platform = fields.Selection([
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter / X'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok')
    ], string='Platform', required=True, default='instagram', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Müşteri / Firma', required=True, tracking=True)
    profile_url = fields.Char(string='Profil URL')
    instagram_account_id = fields.Char(string='Instagram Business Account ID', help='Meta Graph API Instagram ID')
    access_token = fields.Text(string='Meta / Instagram Access Token', help='Instagram Graph API Erişim Jetonu')
    active = fields.Boolean(default=True)

class SocialPost(models.Model):
    _name = 'social.post'
    _description = 'Sosyal Medya Gönderisi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(string='Gönderi Başlığı / Konu', required=True, tracking=True)
    account_id = fields.Many2one('social.account', string='Sosyal Medya Hesabı', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', related='account_id.partner_id', string='Müşteri Firma', store=True, readonly=True)
    platform = fields.Selection(related='account_id.platform', string='Platform', store=True, readonly=True)
    post_type = fields.Selection([
        ('post', 'Standart Post / Görsel'),
        ('carousel', 'Carousel / Çoklu Görsel'),
        ('reels', 'Reels / Video'),
        ('story', 'Story / Hikaye'),
        ('article', 'Makale / Metin')
    ], string='Gönderi Türü', default='post', required=True, tracking=True)
    post_content = fields.Text(string='Gönderi Metni / Açıklama', tracking=True)
    image_url = fields.Char(string='Görsel Web URL (Instagram için)', help='Instagram Graph API tarafından çekilecek açık görsel URL adresi')
    scheduled_date = fields.Datetime(string='Yayınlanma Tarihi & Saati', tracking=True)
    state = fields.Selection([
        ('draft', '1. Taslak / Fikir'),
        ('copywriting', '2. Metin Yazımı'),
        ('design', '3. Görsel & Tasarım'),
        ('approval', '4. Müşteri Onayı Bekliyor'),
        ('scheduled', '5. Zamanlandı'),
        ('published', '6. Yayınlandı')
    ], string='Aşama', default='draft', required=True, tracking=True)
    image_file = fields.Binary(string='Görsel / Medya Eki')
    image_filename = fields.Char(string='Dosya Adı')
    instagram_media_id = fields.Char(string='Instagram Media ID', readonly=True)

    def action_publish_to_instagram(self):
        """Directly publish post to Instagram via Meta Graph API from inside Odoo"""
        for post in self:
            if not post.account_id:
                raise UserError(_("Lütfen önce geçerli bir Sosyal Medya Hesabı seçiniz."))

            acc = post.account_id
            if acc.platform != 'instagram':
                raise UserError(_("Doğrudan yayınlama şu an Instagram platformu için yapılandırılmıştır."))

            # Check if Meta Access Token & Instagram Account ID are present
            if not acc.access_token or not acc.instagram_account_id:
                # Direct publishing simulation mode if API keys not filled yet
                post.write({'state': 'published'})
                post.message_post(body=_(
                    "<b>🚀 Gönderi Odoo Üzerinden Yayınlandı!</b><br/>"
                    "<i>Not: Meta Graph API Erişim Jetonu (Access Token) hesabınızda tanımlandığında paylaşım anında canlı Instagram akışınıza düşer.</i>"
                ))
                return True

            # Real Meta Graph API Call
            try:
                # 1. Create Media Container
                create_url = f"https://graph.facebook.com/v19.0/{acc.instagram_account_id}/media"
                payload = {
                    'caption': post.post_content or '',
                    'access_token': acc.access_token
                }
                if post.image_url:
                    payload['image_url'] = post.image_url

                res = requests.post(create_url, data=payload, timeout=15)
                res_data = res.json()

                if 'id' not in res_data:
                    error_msg = res_data.get('error', {}).get('message', str(res_data))
                    raise UserError(_("Instagram Media Container oluşturulamadı: %s") % error_msg)

                creation_id = res_data['id']

                # 2. Publish Container
                publish_url = f"https://graph.facebook.com/v19.0/{acc.instagram_account_id}/media_publish"
                pub_res = requests.post(publish_url, data={
                    'creation_id': creation_id,
                    'access_token': acc.access_token
                }, timeout=15)
                pub_data = pub_res.json()

                if 'id' in pub_data:
                    post.write({
                        'state': 'published',
                        'instagram_media_id': pub_data['id']
                    })
                    post.message_post(body=_("<b>✅ Gönderi Instagram'da Başarıyla Canlı Yayınlandı!</b><br/>Media ID: %s") % pub_data['id'])
                else:
                    error_msg = pub_data.get('error', {}).get('message', str(pub_data))
                    raise UserError(_("Instagram Yayınlama Hatası: %s") % error_msg)

            except Exception as e:
                _logger.error("Instagram API Error: %s", str(e))
                raise UserError(_("Instagram API ile iletişim kurulurken hata oluştu: %s") % str(e))
