import streamlit as st 
import numpy as np 
import pandas as pd 


########### Utility Functions ##############

def get_stats(team):
    batters, bowlers, all_rounders = [], [], []
    for player in squad[team]:
        player_detail = players_df[players_df['player']==player]#['skill'].values
        if not player_detail.empty:
            skill = player_detail['skill'].values[0]
            if skill == 'BATTER':
                batters.append(player)
            elif skill == 'BOWLER':
                bowlers.append(player)
            elif skill == 'ALL ROUNDER':
                all_rounders.append(player)
            else:
                st.write("Skill not found")
    return {'Batters':batters,'Bowlers':bowlers,'All Rounders':all_rounders}


def get_team_stats(team):
    top_batters,middle_batters,bowlers,wks,others = [], [], [], [], []
    for item in squad[team]:
        player  = item.split('-')[0]
        player_detail = players_df[players_df['player']==player]#['skill'].values
        if not player_detail.empty:
            batting_skill = player_detail['batting_order'].values[0]
            bowling_skill = player_detail['bowling_order'].values[0]
            keeping_skill = player_detail['wicket_keeper'].values[0]
          
            if batting_skill == 'Top':
                top_batters.append(player)
            elif batting_skill == 'Middle':
                middle_batters.append(player)
            elif batting_skill == 'Top/Middle':
                top_batters.append(player)
                middle_batters.append(player)
            else:
                others.append(player)

            if 'Yes' in bowling_skill:
                bowlers.append(player)
            else:
                others.append(player)

            if 'Yes' in keeping_skill:
                wks.append(player)
            else:
                others.append(player)
        else:
            others.append(player)
    return {'Top Order Batters':top_batters,'Middle Order Batter':middle_batters,
            'Key Bowlers':bowlers,'Wicket Keepers':wks}#,'Others':others}


############### Initial Inputs ####################
squad_limit = 15

retention = {'Pdx Panthers':['TANMOY CHANDA-1000','DEV SARKAR-1000',],
            'Blackstone':['SOUVIK DAS-1000','RIJU MUKHERJEE-1000'],
            'Steller Envoy':['AMIK BASU-1000','ANIRBAN SARKAR-1000'],
            'Super Hornets':['SUDIP GHOSH-1000','SANDIP BOSE-1000'],
            'The Bosses':['JAYANTA BARMAN-1000','SUKAMAL SIKDAR-1000'],
            'Flying Falcons':['SOURAV BISWAS-1000','SIBOTOSH BARUI-1000']}

if 'squad' not in st.session_state:
    st.session_state.squad = retention
squad = st.session_state.squad


wallet = {'Pdx Panthers':7200,'Blackstone':5950,
          'Steller Envoy':6900,'Super Hornets':8550,
          'The Bosses':8800,'Flying Falcons':9700}

if 'balance' not in st.session_state:
    st.session_state.balance = wallet
balance = st.session_state.balance


if 'rtm' not in st.session_state:
    st.session_state.rtm = {'Pdx Panthers':1,'Blackstone':1,
                            'Steller Envoy':1,'Super Hornets':1,
                            'The Bosses':1,'Flying Falcons':1}
rtm_available = st.session_state.rtm



st.title('Player Auction App - 2024')

squad_size = {team: len(squad[team]) for team in squad.keys()}
rtm_balance = {k:'Yes' if v>0 else 'No' for k,v in rtm_available.items()}
go_upto = {team:balance[team]-(squad_limit-squad_size[team])*100 for team in squad.keys()}
st.table(pd.DataFrame({'Squad Size':squad_size,'Balance':balance,
                       'Has RTM?':rtm_balance,'Can Go Upto':go_upto}).T)



st.subheader("Auction Panel")
players_df = pd.read_csv("/home/aniruddha/Programs/Game Auction App/player_list.csv")
players_df['bowling_order'] = players_df['bowling_order'].astype('str')
players_df['batting_order'] = players_df['batting_order'].astype('str')
players_df['wicket_keeper'] = players_df['wicket_keeper'].astype('str')

######### Fetching the Unsold Players ############################
if 'unsold_players' not in st.session_state:
    st.session_state.unsold_players = players_df['player'].groupby(players_df['pool']).apply(list).to_dict()
unsold_players = st.session_state.unsold_players


######### Fetching the Sold Players ########################################
if 'sold_players' not in st.session_state:
    st.session_state.sold_players = []
    for items in squad.values():
        st.session_state.sold_players.extend(item.split('-')[0] for item in items)


sold_players = st.session_state.sold_players

sold_players_grouped = {}
for item in sold_players:
    pool = players_df[players_df['player']==item]['pool'].values[0]
    if pool in sold_players_grouped.keys():
        sold_players_grouped[pool].append(item)
    else:
        sold_players_grouped[pool] = [item]


################### Auction Panel UI ############################
col1, col2 = st.columns(2)
with col1:
    pool_names = players_df['pool'].unique()
    pool = st.selectbox('Select Player Pool',pool_names)
with col2:
    player = st.selectbox("Select Player ({} players are left in **{}** pool)"\
                          .format(len(unsold_players[pool])-len(sold_players_grouped[pool]),pool)\
                          ,players_df[players_df['pool']==pool])

st.write(players_df[players_df['player']==player])

#################### RTM check #################
previous_team = players_df[players_df['player']==player]["previous_team"].values[0]
if previous_team in squad.keys():
    st.write("**RTM is available to**",previous_team)
else:
    pass

col1, col2, col3 = st.columns(3)
with col1:
    sold_to = st.selectbox('Sold to',squad.keys())

with col2:
    sell_price = st.number_input('Sell Price',min_value=100,max_value=6000,step=100)

with col3:
    rtm_used = st.selectbox('RTM Used?',['No','Yes'])

max_bid = players_df[players_df['player']==player]['max_bid'].values[0]

######### Logging ##############################################
message1 = '{} has been sold to {} for Rs.{} '.format(player,sold_to,sell_price)
message2 = '{} has been sold to ** PDX PANTHERS ** for {} with margin of ---------> Rs.{}'\
            .format(player,sell_price,max_bid-sell_price)

if 'logs' not in st.session_state:
    st.session_state.logs = []
logs = st.session_state.logs


##################### The Selling Function ############################
col1, col2, col3 = st.columns(3)
with col2:
    if submit:= st.button('Sell **{}** -> **{}**'.format(player,sold_to),type='primary',use_container_width=True):
        if player in sold_players:
            st.error('{} is already sold !!!'.format(player))
            st.stop()
        else:
            if rtm_used == 'Yes' and rtm_available[sold_to] > 0:
                rtm_available[sold_to] -= 1
                squad[sold_to].append(player + '-' + str(sell_price))
                balance[sold_to] -= sell_price

                if sold_to == 'Pdx Panthers':
                    logs.append(message2 +'--------------- RTM* used')
                else:
                    logs.append(message1 +'--------------- RTM* used')

            elif rtm_used == 'Yes' and rtm_available[sold_to] < 1:
                st.error('RTM not available to {}'.format(sold_to))
                st.stop()
            else:
                squad[sold_to].append(player + '-' + str(sell_price))
                balance[sold_to] -= sell_price

                if sold_to == 'Pdx Panthers':
                    logs.append(message2)
                else:
                    logs.append(message1)
        
        unsold_players[pool].remove(player)
        sold_players.append(player)

        st.session_state.logs = logs
        st.session_state.squad = squad
        st.session_state.balance = balance
        st.session_state.rtm = rtm_available
        st.session_state.unsold_players = unsold_players
        st.session_state.sold_players = sold_players


########### Squad Capability Details ############################
col1, col2 = st.columns(2)
with col1:
    st.subheader('Squad Capability Details')
with col2:
    franchise = st.selectbox('Select Team',squad.keys())

my_team = get_team_stats(franchise)
# st.table(my_team)
skill_columns = list(my_team.keys())
for col in st.columns(len(skill_columns)):
    with col:
        skill = skill_columns[int(str(col.__dict__['_provided_cursor'])[-3])]
        # st.write('**{}**'.format(skill))
        st.table(pd.DataFrame(my_team[skill],columns=[skill]))


############### All Squad Players List ############################
st.subheader('All Squad Player List')

columns = list(retention.keys())
for col in st.columns(len(columns)):
    with col:
        team = columns[int(str(col.__dict__['_provided_cursor'])[-3])]
        st.write('**{}** - {}/{}'.format(team,len(squad[team]),squad_limit))
        st.table(pd.DataFrame(squad[team],columns=[team]))



st.subheader('Auction Logs')
st.write(logs)