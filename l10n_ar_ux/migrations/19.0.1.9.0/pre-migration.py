import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Remove external IDs of account.account.tags that are still in use,
    to prevent Odoo from trying to delete them during upgrade."""
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
            continue
        tag_id = row[0]
        cr.execute("""
            SELECT 1 FROM account_account_tag_account_tax_repartition_line_rel
            WHERE account_account_tag_id = %s LIMIT 1
        """, (tag_id,))
        if cr.fetchone():
            cr.execute("""
                DELETE FROM ir_model_data
                WHERE module = 'l10n_ar_ux' AND name = %s
            """, (name,))
            _logger.info("Removed external ID l10n_ar_ux.%s (tag in use)", name)
