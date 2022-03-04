import streamlit as st
import pandas as pd

inter_list = ['-']

def selector(start, df_rel, cond, dfr, dfo_ind):

    global selection, gl_config_error

    
    df_cur = dfr[dfr['From'] == start]
    df_cur = df_cur[df_cur['Relation type'].isin(df_rel)]
    df_cur = df_cur[df_cur['Condition'].isin(cond)]

    if len(df_cur) != 0:

        for r in df_cur.iterrows():
            if r[1]['XOR ID'] == '-':
                dfo_ind.loc[start, 'highlight_type'] = 'intermediate'
    
                selector(r[1]['To'], df_rel, cond, dfr, dfo_ind)

            else:
                df_xor = df_cur[df_cur['XOR ID'] == r[1]['XOR ID']]
                default = 'True'
                choice = []
                choice_cond = ''


                for n in df_xor.iterrows():
                  if n[1]['Condition'] == '-' and default == 'True':
                    choice = n[1]['To']

                  elif n[1]['Condition'] in cond and default == 'False':
                    gl_config_error = '>>> ERROR:','ambiguous selection. {}-{} with {}-{} for parent object {}'.format(n[1]['To'], n[1]['Condition'], choice, choice_cond,start)
                    return

                  elif n[1]['Condition'] in cond and default == 'True':
                    default = 'False'
                    choice = n[1]['To']
                    choice_cond = n[1]['Condition']

                  else:
                    choice = False

                if choice:
                    dfo_ind.loc[start, 'highlight_type'] = 'intermediate'
                    selector(choice, df_rel, cond, dfr, dfo_ind)

                else:
                  selection.append(start)

    else:
        selection.append(start)
        
def set_object_color(st, sel, dfo):
    color_list = []
    
    for i in dfo.iterrows():

        if (i[1]['Object ID'] == st):
            color_list.append('start')
        else:
            if (i[1]['Object ID'] in sel):
                color_list.append('selected')
                
            elif i[1]['highlight_type'] != 'intermediate':
                color_list.append('-')
            else:
                color_list.append('intermediate')
                
    return color_list
                
depth = 0
def recur_4x (d, oid, dfr):     
    """
    recursive function to set the x-values for all Objects
    """
    global depth

    if (d < depth):
        depth = d
        
    tdf = dfr[dfr['From'] == oid]
    
    if (len(tdf) > 0):
        for j, r in tdf.iterrows():
            m = recur_4x(d-1, tdf['To'][j], dfr)
            
            if (m < depth):
                depth = m
    return depth

                

header = st.container()
descriptive = st.container()
uploads = st.container()
dropdowns = st.container()
output_table = st.container()
dropdowns2 = st.container()
output_table2 = st.container()




with header:
  st.title('Sketch 4')
  
with descriptive:
  st.markdown(
    """
    ---
    #### Functionality:
    The program automatically adds inverse relations to the list relations.csv.
    
    Note: normal and their inverse relations should not be selected at the same time. 
    This will cause infinite loops of the program.
    
    ---
    """
  )
  
with uploads:

    l_col, r_col = st.columns(2)
        
    objects_u = l_col.file_uploader('Upload Objects', 
                                    accept_multiple_files = False, 
                                    type = 'CSV')
    if objects_u is not None:
        df_obj = pd.read_csv(objects_u)
        df_obj = df_obj.fillna("-")

    relations_u = r_col.file_uploader('Upload Relations', 
                                        accept_multiple_files = False, 
                                        type = 'CSV')
    if relations_u is not None:
        df_rel = pd.read_csv(relations_u)
        df_rel = df_rel.fillna("-")
        
        df_inv_rel = pd.DataFrame()
        for i, r in df_rel.iterrows():
            irid    = r['Relation ID'] + ".i"          # inverse relation 'id'
            irfrom  = r['To']                           # inverse relation 'From'
            irrtype = "(inverse) " + r['Relation type']
            irxor   = r['XOR ID']
            irto    = r['From']
            ircond  = r['Condition']
            irrtt   = r['RelTypeType']
            newrel  = { "Relation ID": irid, 
                       "From": irfrom, 
                       "Relation type": irrtype, 
                       "XOR ID": irxor, 
                       "To": irto, 
                       "Condition": ircond, 
                       "RelTypeType": irrtt }
            try:
                df_inv_rel = df_inv_rel.append(newrel, ignore_index=True)
            except:
                # print("Hmm...")
                pass
        df_rel = df_rel.append(df_inv_rel, ignore_index = True)
        
    
with dropdowns:
    l_col, m_col, r_col = st.columns(3)

    if objects_u is not None:
        if 'Object ID' not in df_obj.columns:
            l_col.write('No object ID column found')
        else:
            start_obj = l_col.selectbox('Start object', 
                        options = df_obj['Object ID'])
    else:
        start_obj = l_col.selectbox('Start object', 
                        options = ['No objects found'])
        
    if relations_u is not None:
        conditions = m_col.multiselect('Conditions', 
                                    options = list(filter(lambda a: a != '-', df_rel['Condition'].unique())))
    else:
        conditions = m_col.multiselect('Conditions', 
                                    options = ['No conditions found'],
                                    default = ['No conditions found'])
        
    if relations_u is not None:
        
                
        rel_types = r_col.multiselect('Relation types', 
                                      
                                    options = df_rel['Relation type'].unique(),
                                    default = df_rel['Relation type'].unique()[0])
        inv_selected = []
        for t in rel_types:
            if t[0] == '(':
                inv_selected.append(t[10:])
            else:
                inv_selected.append('(inverse) {}'.format(t))
                
        for t in rel_types:
            if t in inv_selected:
                st.error("Error, can't select both the normal AND inverse relation of the same type.")
                break
        df_rel = df_rel.loc[~df_rel['Relation type'].isin(inv_selected)]


    else:
        rel_types = r_col.multiselect('Relation types', 
                                    options = ['No relations found'], 
                                    default = ['No relations found'])
                

    
    
        
with output_table:
            
    if objects_u is not None and relations_u is not None:
        if conditions is None:
            cds = ['-']
        else:
            cds = conditions.append('-')
            selection = []
            gl_config_error = ''
            
            df_obj = df_obj.set_index('Object ID')
            df_obj['highlight_type'] = '-'
            selector(start_obj, rel_types, conditions, df_rel, df_obj)
            df_obj = df_obj.reset_index()
            col_list = set_object_color(start_obj, selection, df_obj)
            df_obj['highlight_type'] = col_list
            
            
            st.subheader('Output table')
            

            
            
            if gl_config_error != '':
                st.write(gl_config_error)
            
                st.table()
            else:
                df_results = df_obj[df_obj['highlight_type'] != '-']
                df_results['highlight_type'] = pd.Categorical(df_results['highlight_type'], 
                                                            ['start', 'intermediate', 'selected'])
                df_results = df_results.sort_values('highlight_type')
                df_results = df_results[['Object ID', 
                                        'Object type3', 
                                        'highlight_type']].reset_index(drop = True)
                df_results.index += 1
                st.table(df_results)
                
                

with dropdowns2:
    results = []
    l_col2, m_col2, r_col2 = st.columns(3)

    if objects_u is not None:
        if 'Object ID' not in df_obj.columns:
            l_col2.write('No object ID column found')
        else:
            start_obj2 = l_col2.selectbox('Assembly Object', 
                        options = df_obj['Object ID'])
    else:
        start_obj2 = l_col2.selectbox('Assembly Object', 
                        options = ['No objects found'])
        
    if relations_u is not None:
        
                
        rel_types2 = r_col2.multiselect('Assembly Relation(s)', 
                                      
                                    options = df_rel['Relation type'].unique(),
                                    default = df_rel['Relation type'].unique()[0])
        inv_selected2 = []
        for t in rel_types2:
            if t[0] == '(':
                inv_selected2.append(t[10:])
            else:
                inv_selected2.append('(inverse) {}'.format(t))
                
        for t in rel_types:
            if t in inv_selected2:
                st.error("Error, can't select both the normal AND inverse relation of the same type.")
                break
        df_rel = df_rel.loc[~df_rel['Relation type'].isin(inv_selected2)]


    else:
        rel_types = r_col.multiselect('Assembly Relation(s)', 
                                    options = ['No relations found'], 
                                    default = ['No relations found'])

with output_table2:
            
    if objects_u is not None and relations_u is not None:
        if conditions is None:
            cds = ['-']
        else:
            cds = conditions.append('-')
            selection = []
            gl_config_error = ''
            
            df_obj2 = df_obj.set_index('Object ID')
            df_obj2['highlight_type'] = '-'
            selector(start_obj2, rel_types2, conditions, df_rel, df_obj2)
            df_obj2 = df_obj2.reset_index()
            col_list = set_object_color(start_obj2, selection, df_obj2)
            df_obj2['highlight_type'] = col_list
            
            df_obj2 = pd.merge(df_obj2, df_obj, how='inner')

            st.subheader('Assembly Elements')
            
            if gl_config_error != '':
                st.write(gl_config_error)
            
                st.table()
            else:
                df_results = df_obj2[df_obj2['highlight_type'] != '-']
                df_results['highlight_type'] = pd.Categorical(df_results['highlight_type'], 
                                                            ['start', 'intermediate', 'selected'])
                df_results = df_results.sort_values('highlight_type')
                df_results = df_results[['Object ID', 
                                        'Object type3', 
                                        'highlight_type']].reset_index(drop = True)
                df_results.index += 1
                st.table(df_results)