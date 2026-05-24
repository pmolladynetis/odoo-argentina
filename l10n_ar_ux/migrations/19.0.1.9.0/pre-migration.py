import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Remove external IDs and FK references of account.account.tags that are
    still in use, to prevent Odoo from trying to delete them during upgrade."""
    xml_id_names = [
        "tag_ret_perc_sicore_aplicada",
        "tax_tag_a_cuenta_iibb",
    ]
    for name in xml_id_names:
        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE module = 'l10n_ar_ux' AND name = %s
            AND model = 'account.account.tag'
        """, (name,))
        row = cr.fetchone()
        if not row:
            _logger.info("External ID l10n_ar_ux.%s not found, skipping", name)
            continue
        tag_id = row[0]
        # Remove the FK reference so Odoo can safely process this tag
        cr.execute("""
            DELETE FROM account_account_tag_account_tax_repartition_line_rel
            WHERE account_account_tag_id = %s
        """, (tag_id,))
        _logger.info("Removed %s FK references for tag id=%s (%s)", cr.rowcount, tag_id, name)
        # Remove the external ID so Odoo doesn't try to delete the tag
        cr.execute("""
            DELETE FROM ir_model_data
            WHERE module = 'l10n_ar_ux' AND name = %s
        """, (name,))
        _logger.info("Removed external ID l10n_ar_ux.%s", name)
