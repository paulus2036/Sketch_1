import streamlit as st
import pandas as pd

objects = pd.read_csv('data/dataset003/objects-003.csv')
relations = pd.read_csv('data/dataset003/relations-003.csv')

selection = []

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
uploads = st.container()
dropdowns = st.container()

# dataset = st.beta_container()



menu = ['Sketch 1', 'Sketch 2']
choice = st.sidebar.radio("Menu", menu)

if choice == "Sketch 1":
  with header:
    st.title('Sketch 1')
    
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
      
  with dropdowns:
    results = []
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
    else:
      rel_types = r_col.multiselect('Relation types', 
                                    options = ['No relations found'], 
                                    default = ['No relations found'])
      
      
    if objects_u is not None and relations_u is not None:
      if conditions is None:
        cds = ['-']
      else:
        cds = conditions.append('-')
        
      selection = []
      selector(start_obj, rel_types, conditions, df_rel, df_obj)
      results = selection
      
      st.subheader('Output table')
      df_results = pd.DataFrame(set(selection), columns=['Selected items'])
      df_results.index += 1
      st.table(df_results)

if choice == "Sketch 2":
  with header:
    st.title('Sketch 2')
































































