FROM odoo:17.0

USER root

# Copy custom entrypoint and setup scripts
COPY ./entrypoint.sh /entrypoint.sh
COPY ./render_auto_setup.py /etc/odoo/render_auto_setup.py
RUN chmod +x /entrypoint.sh

# Copy custom addons
COPY ./addons /mnt/extra-addons

# Copy configuration
COPY ./odoo.conf /etc/odoo/odoo.conf

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf /etc/odoo/render_auto_setup.py /entrypoint.sh

USER odoo

EXPOSE 8069

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
