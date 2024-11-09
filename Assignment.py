import pandas as pd
from datetime import datetime
import re

# def total_loyalty_points(loyalty_dataframe):
#     user_id = []
#     loyalty_points = []
#     no_of_games_played = []
#     for index, row in loyalty_dataframe.iterrows():
#         user_id.append(row['User Id'])
#         no_of_games_played.append(row['No of Games Played'])
#         points = row['Loyalty Points'] + 0.001*max((row['Deposit Counts']-row['Withdrawal Counts']),0)
#         loyalty_points.append(points)
#     final_loyalty_points = pd.DataFrame({'User Id':user_id, 'Loyalty Points':loyalty_points, 'No of Games Played':no_of_games_played}, columns=['User Id', 'Loyalty Points', 'No of Games Played'])
#     final_loyalty_points = final_loyalty_points.sort_values(by=['Loyalty Points','No of Games Played'], ascending=[False, True]).reset_index(drop=True)
#     return final_loyalty_points

def total_loyalty_points(loyalty_dataframe):
    loyalty_dataframe['Adjusted Loyalty Points'] = (
        loyalty_dataframe['Loyalty Points'] + 
        0.001 * (loyalty_dataframe['Deposit Counts'] - loyalty_dataframe['Withdrawal Counts']).clip(lower=0)
    )

    final_loyalty_points = (
        loyalty_dataframe[['User Id', 'Adjusted Loyalty Points', 'No of Games Played']]
        .sort_values(by=['Adjusted Loyalty Points', 'No of Games Played'], ascending=[False, True])
        .reset_index(drop=True)
    )

    final_loyalty_points.rename(columns={'Adjusted Loyalty Points': 'Loyalty Points'}, inplace=True)
    return final_loyalty_points

def loyalty_points(user_dataframe, column1, loyalty_points_types):
    if loyalty_points_types == 'Games Played':
        user_dataframe['Loyalty Points'] = user_dataframe[column1].map(lambda x: x*0.2)
    elif loyalty_points_types == 'Deposit Amount':
        user_dataframe['Loyalty Points'] = user_dataframe[column1].map(lambda x: x*0.01)
    else:
        user_dataframe['Loyalty Points'] = user_dataframe[column1].map(lambda x: x*0.005)
    return user_dataframe
    
# def average_monthly_deposit_amount_per_user():
#     unique_users = []
#     average_amount = []
#     for index, row in deposit_data.iterrows():
#         if row['User Id'] not in unique_users:
#             unique_users.append(row['User Id'])
#             average_amount.append(row['Amount'])
#         else:
#             average_amount[unique_users.index(row['User Id'])] = average_amount[unique_users.index(row['User Id'])] + row['Amount']
#     for i in unique_users:
#         count = len(deposit_data[deposit_data['User Id'].map(lambda x: x==i)])
#         average_amount[unique_users.index(i)] = int(average_amount[unique_users.index(i)]/count) + (average_amount[unique_users.index(i)] % count > 0 )
#     return pd.DataFrame({"User Id": unique_users, "Average Amount": average_amount}, columns=['User Id', 'Average Amount'])

def average_monthly_deposit_amount_per_user(deposit_data):
    deposit_amount_per_user = pd.DataFrame({'User Id':deposit_data['User Id'],'Amount':deposit_data['Amount']}, columns=['User Id', 'Amount'])
    avg_games = deposit_amount_per_user.groupby('User Id').agg('mean').reset_index()
    avg_games.columns = ['User ID', 'Average Amount Deposited']
    temp_dataframe = deposit_amount_per_user['User Id'].unique()
    average_deposited_amount_by_user = pd.DataFrame({'User Id': temp_dataframe, 'Average Amount Deposited':avg_games['Average Amount Deposited']}, columns=['User Id','Average Amount Deposited'])
    return average_deposited_amount_by_user

def average_monthly_deposit(deposit_data):
    return deposit_data['Amount'].agg('mean')

def games_played_per_user(user_data):
    user_played = pd.DataFrame({'User Id':user_data['User ID'],'Games Played':user_data['Games Played']}, columns=['User Id', 'Games Played'])
    avg_games = user_played.groupby('User Id').sum().reset_index()
    avg_games.columns = ['User ID', 'Total Games Played Per User']
    temp_dataframe = user_played['User Id'].unique()
    games_played = pd.DataFrame({'User Id': temp_dataframe, 'Games Played Per User':avg_games['Total Games Played Per User']}, columns=['User Id','Games Played Per User'])
    return games_played

def sum_of_data(user_dataframe, column1, column2):
    user_data1 = pd.DataFrame({column1:user_dataframe[column1],column2:user_dataframe[column2]}, columns=[column1, column2])
    sum_of_dataframe = user_data1.groupby(column1).sum().reset_index()
    sum_of_dataframe.columns = [column1, column2]
    temp_dataframe = user_data1[column1].unique()
    sum_of_data2 = pd.DataFrame({column1: temp_dataframe, column2:sum_of_dataframe[column2]}, columns=[column1,column2])
    return sum_of_data2

def loyalty_points_per_user(user_data, deposit_data, withdrawal_data):
    deposit_user_id_counts  = deposit_data['User Id'].value_counts().reset_index(name='Counts')
    withdrawal_user_id_counts = withdrawal_data['User Id'].value_counts().reset_index(name='Counts')
    deposit_amount = sum_of_data(deposit_data, 'User Id', 'Amount')
    df = loyalty_points(deposit_amount, 'Amount', 'Deposit Amount')
    user_id_counts_map = deposit_user_id_counts.set_index('User Id')['Counts']
    df['Deposit Counts'] = df['User Id'].map(user_id_counts_map)
    withdrawal_amount = sum_of_data(withdrawal_data, 'User Id', 'Amount')
    df2 = loyalty_points(withdrawal_amount, 'Amount', 'Withdrawal Amount')
    withdrawal_user_id_counts_map = withdrawal_user_id_counts.set_index('User Id')['Counts']
    df2['Withdrawal Counts'] = df2['User Id'].map(withdrawal_user_id_counts_map)
    user_games_played = sum_of_data(user_data, 'User ID', 'Games Played')
    df3 = loyalty_points(user_games_played, 'Games Played', 'Games Played')
    user_loyalty_points = pd.DataFrame({
        "User Id": df['User Id'],
        "Loyalty Points": df['Loyalty Points'],
        "Deposit Counts": df['Deposit Counts']
    }, columns= ['User Id', 'Loyalty Points','Deposit Counts','Withdrawal Counts'])
    for index, row in df2.iterrows():
        if row['User Id'] not in user_loyalty_points['User Id'].values:
            new_row = pd.DataFrame([{'User Id': row['User Id'], 'Loyalty Points': row['Loyalty Points'], 'Withdrawal Counts': row['Withdrawal Counts']}])
            user_loyalty_points = pd.concat([user_loyalty_points, new_row], ignore_index=True)
        else:
            index1 = user_loyalty_points.index[user_loyalty_points['User Id'] == row['User Id']].values
            if len(index1) > 0:
                user_loyalty_points.at[index1[0], 'Loyalty Points'] = user_loyalty_points.at[index1[0], 'Loyalty Points'] + row['Loyalty Points']
                user_loyalty_points.at[index1[0], 'Withdrawal Counts'] = row['Withdrawal Counts']
            else:
                print(row['User Id'])
                print("Index Not Found")

    for index, row in df3.iterrows():
        if row['User ID'] not in user_loyalty_points['User Id'].values:
            new_row = pd.DataFrame([{'User Id': row['User ID'], 'Loyalty Points': row['Loyalty Points'], 'No of Games Played':row['Games Played'],'Deposit Counts': 0, 'Withdrawal Counts': 0}])
            user_loyalty_points = pd.concat([user_loyalty_points, new_row], ignore_index=True)
        else:
            index1 = user_loyalty_points.index[user_loyalty_points['User Id'] == row['User ID']].values
            if len(index1) > 0:
                user_loyalty_points.at[index1[0], 'No of Games Played'] = row['Games Played']
                user_loyalty_points.at[index1[0], 'Loyalty Points'] = user_loyalty_points.at[index1[0], 'Loyalty Points'] + row['Loyalty Points']
            else:
                print(row['User ID'])
                print("Index Not Found")

    user_loyalty_points = user_loyalty_points.fillna(0)
    user_loyalty_points = user_loyalty_points.astype(int)
    return user_loyalty_points

def datetime_dataframe(df, datetime_slot):
    df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d-%m-%Y %H:%M', errors='coerce')
    datetime_parts = datetime_slot.split()

    date = datetime_parts[0]
    date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date)
    month = datetime.strptime(datetime_parts[1], "%B").month
    slot = " ".join(datetime_parts[2:])
    slot = slot.rstrip()
    slot = slot.strip()
    date = date + '-' + str(month) + '-2022'
    if slot == 'Slot S1':
        start_date = pd.to_datetime(str(date + ' 00:00:00'), format='%d-%m-%Y %H:%M:%S', errors='coerce')
        end_date = pd.to_datetime(str(date + ' 11:59:59'), format='%d-%m-%Y %H:%M:%S', errors='coerce')
        print(start_date, end_date)
        filtered_df = df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
    else: 
        start_date = pd.to_datetime(str(date + ' 12:00:00'), format='%d-%m-%Y %H:%M:%S', errors='coerce')
        end_date = pd.to_datetime(str(date + ' 23:59:59'), format='%d-%m-%Y %H:%M:%S', errors='coerce')
        filtered_df = df[(df['Datetime'] >= start_date) & (df['Datetime'] <= end_date)]
    return filtered_df

def slot_wise_loyalty_points(user_data, deposit_data, withdrawal_data, date_slot_string):
    user_data = datetime_dataframe(user_data, date_slot_string)
    deposit_data = datetime_dataframe(deposit_data, date_slot_string)
    withdrawal_data = datetime_dataframe(withdrawal_data, date_slot_string)
    user_loyalty_points = loyalty_points_per_user(user_data, deposit_data, withdrawal_data)
    user_loyalty_points = total_loyalty_points(user_loyalty_points)
    return user_loyalty_points

def loyalty_bonus_share(user_loyalty_points):
    total_loyalty_bonus = 50000
    total_loyalty_points = user_loyalty_points['Loyalty Points'].sum()
    user_loyalty_points['Bonus Share'] = (user_loyalty_points['Loyalty Points'] / total_loyalty_points) * total_loyalty_bonus
    user_loyalty_points['Bonus Share'] = user_loyalty_points['Bonus Share'].round().astype(int)
    return user_loyalty_points[['User Id', 'Loyalty Points', 'No of Games Played', 'Bonus Share']]

def main(user_data, deposit_data, withdrawal_data):
    while True:
        print("\nMain Menu:")
        print("1. Slot Wise Loyalty Points Earned by Player")
        print("2. Ranking Player on the basis of Loyalty Points")
        print("3. Top 50 Ranking Player")
        print("4. Average Deposit Amount")
        print("5. Average Deposit Amount Per User in a month")
        print("6. Total Number of Games Played Per User in a month")
        print("7. Loyalty Bonus Share into Top 50 Players")
        print("8. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            input_string = input("Enter the date and slot Eg. \'16th October Slot S2\':")
            print(slot_wise_loyalty_points(user_data, deposit_data, withdrawal_data, input_string))

        elif choice == '2':
            user_loyalty_points = loyalty_points_per_user(user_data, deposit_data, withdrawal_data)
            user_loyalty_points = total_loyalty_points(user_loyalty_points)
            print(user_loyalty_points)
        elif choice == '3':
            user_loyalty_points = loyalty_points_per_user(user_data, deposit_data, withdrawal_data)
            user_loyalty_points = total_loyalty_points(user_loyalty_points)
            print(user_loyalty_points.head(50))
            break
        elif choice == '4':
            average_monthly_deposit_value = round(average_monthly_deposit(deposit_data), 2)
            print(average_monthly_deposit_value)
            break
        elif choice == '5':
            print(average_monthly_deposit_amount_per_user(deposit_data))
            break
        elif choice == '6':
            total_games_played_per_user = games_played_per_user(user_data)
            print(total_games_played_per_user)
            break
        elif choice == '7':
            user_loyalty_points = loyalty_points_per_user(user_data, deposit_data, withdrawal_data)
            user_loyalty_points = total_loyalty_points(user_loyalty_points)
            user_loyalty_points = loyalty_bonus_share(user_loyalty_points.head(50))
            print(user_loyalty_points)
            break
        elif choice == '8':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__=="__main__":
    df = pd.read_excel("./Analytics Position Case Study.xlsx", sheet_name=["User Gameplay data", "Deposit Data", "Withdrawal Data"], skiprows=3, index_col=None, na_values=['NA']) 
    user_data, deposit_data, withdrawal_data = df["User Gameplay data"], df["Deposit Data"], df["Withdrawal Data"]
    
    main(user_data, deposit_data, withdrawal_data)