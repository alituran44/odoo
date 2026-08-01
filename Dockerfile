FROM odoo:17.0

USER root

# Copy custom entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Copy configuration
COPY ./odoo.conf /etc/odoo/odoo.conf

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf /entrypoint.sh

USER odoo

EXPOSE 8069

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
