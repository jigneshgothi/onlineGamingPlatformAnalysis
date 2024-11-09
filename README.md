Here I have created Menu where select a particular option for your queries.

1. Slot Wise Loyalty Points Earned by Player
2. Ranking Player on the basis of Loyalty Points
3. Top 50 Ranking Player
4. Average Deposit Amount
5. Average Deposit Amount Per User in a month
6. Total Number of Games Played Per User in a month
7. Loyalty Bonus Share into Top 50 Players
8. Exit

Top 50 Player Bonus Share:
Formula: player_loyalty_points/total_loyalty_points(top 50) * Bnous Amount

I think that this is a best formula to calculate the loyalty points of the players where we are focusing on Deposited amount, withdrawal amount, No. of Games played by the user and ratio of counts of deposit and withdrawal by the user.
Here I think that for calculating the loyalty points, we can add no. of wins and no. of loose. in a formula.

Loyalty Point = max((No of Wins - No of Loose), 0) + (0.01 * deposit) + (0.005 * Withdrawal amount) + (0.001 * (maximum of (#deposit - #withdrawal) or 0)) + (0.2 * Number of games played)
