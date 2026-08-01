FROM odoo:17.0

USER root

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Copy configuration
COPY ./odoo.conf /etc/odoo/odoo.conf

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

USER odoo

EXPOSE 8069 8072

CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
