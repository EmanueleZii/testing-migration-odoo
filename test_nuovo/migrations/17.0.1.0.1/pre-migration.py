from openupgradelib import openupgrade

def migrate(cr, version):
    old_model = 'test.vecchio'
    new_model = 'test.nuovo'
    old_table = 'test_vecchio'
    new_table = 'test_nuovo'
    
    if openupgrade.table_exists(cr,old_table):
        cr.execute(f"ALTER TABLE {old_table} RENAME TO {new_table}")
        print(f"--- SQL: Tabella {old_table} rinominata in {new_table}")
        
        
    cr.execute("""
            UPDATE ir_model_data
            SET model = %s
            WHERE model = %s
            """, (new_model, old_model))
    
    
    cr.execute("""
            UPDATE ir_model_data
            SET model = 'test_nuovo'
            WHERE model = 'test_vecchio'
            """)
    
    
    openupgrade.rename_models(cr, [(old_model, new_model)])
    
    cr.execute("UPDATE ir_module_module SET state='to remove' WHERE name='test_vecchio'")