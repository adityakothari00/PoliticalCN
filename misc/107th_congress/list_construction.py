import pandas as pd
import networkx as nx
from itertools import combinations

#Set the threshold for near-unanimous votes at 90% one sided
unanimousThreshold = 0.90

#Read in the votes data
votes = pd.read_csv("S107_votes.csv")


votes = votes[["congress", "chamber", "rollnumber", "icpsr", "cast_code"]].copy()

#Sets that if code is 1,2,3 it is a yea vote, if it is 4,5,6 it is a nay vote, 
#and if it is 7 or 8 it is an abstention
def encode_vote(code):
    if code in [1, 2, 3]:
        return 1
    elif code in [4, 5, 6]:
        return -1
    else:
        return 0
    
#Create a new column in the votes dataframe that encodes the votes as 1, -1, or 0
votes["voteVal"] = votes["cast_code"].apply(encode_vote)

print(votes)

#Create a new dataframe that only contains substantive votes (no abstentions or such)
substantiveVotes = votes[votes["voteVal"] != 0].copy()


#Create a summary dataframe that counts the number of yea and nay votes for each roll call
rollcallSummary = (substantiveVotes.groupby("rollnumber")["voteVal"].agg(
        yeaCount=lambda x: (x == 1).sum(),
        nayCount=lambda x: (x == -1).sum()
    )
    .reset_index()
)

#Adds a column to the rollcall summary that is the total amount of substantive votes for each roll call
rollcallSummary["totalSubstantive"] = rollcallSummary["yeaCount"] + rollcallSummary["nayCount"]

#Adds a column to the rollcall summary that is the fraction of votes that are in the majority 
#(either yea or nay). Used to filter out near-unanimous votes.
rollcallSummary["majorityFrac"] = rollcallSummary[["yeaCount", "nayCount"]].max(axis=1) / rollcallSummary["totalSubstantive"]

#Filters the roll calls to only keep those that are not near-unanimous
filteredRollcalls = rollcallSummary.loc[rollcallSummary["majorityFrac"] <= unanimousThreshold, "rollnumber"]


#Filters votes to only include the roll calls that are not near-unanimous
votes = votes[votes["rollnumber"].isin(filteredRollcalls)].copy()


#Prints out a summary of the outcome of thefiltering process
print(f"Threshold: {unanimousThreshold}")
print(f"# of original roll calls: {rollcallSummary.shape[0]}")
print(f"# of kept roll calls: {len(filteredRollcalls)}")
print(f"# of dropped roll calls: {rollcallSummary.shape[0] - len(filteredRollcalls)}")


#Creates a vote matrix where rows are legislators, columns are roll calls, and values are the encoded votes (1, -1, or 0)
voteMatrix = votes.pivot_table(index="icpsr", columns="rollnumber", values="voteVal", fill_value=0)

print(voteMatrix.head())

senators = voteMatrix.index.tolist()

edges = []


#Loops through all pairs of senators
for senator1, senator2 in combinations(senators, 2):
    votes1 = voteMatrix.loc[senator1]
    votes2 = voteMatrix.loc[senator2]

    bothVoted = (votes1 != 0) & (votes2 != 0)

    if bothVoted.sum() == 0:
        continue

    votes1Common = votes1[bothVoted]
    votes2Common = votes2[bothVoted]


    agreementCount = (votes1Common == votes2Common).sum()
    disagreementCount = (votes1Common != votes2Common).sum()
    totalVotes = agreementCount + disagreementCount

    #Calculates signed weightage and agreement fraction
    signedWeightage = (agreementCount - disagreementCount)
    agreementFraction = agreementCount / totalVotes


    #Adds edge record to the list
    edges.append({
        "source": senator1,
        "target": senator2,
        "agreement_count": agreementCount,
        "disagreement_count": disagreementCount,
        "total_votes": totalVotes,
        "signed_weight": signedWeightage,
        "agreement_fraction": agreementFraction
    })

edges_df = pd.DataFrame(edges)
print(edges_df.head())


gPositive = nx.Graph()

for senator in senators:
    gPositive.add_node(senator)

for _, row in edges_df.iterrows():
    if row["signed_weight"] > 0:
        gPositive.add_edge(
            row["source"],
            row["target"],
            weight=row["agreement_fraction"],
        )

print(gPositive.number_of_nodes(), gPositive.number_of_edges())

members = pd.read_csv("S107_members.csv")
members = members[["icpsr", "bioname", "party_code", "state_abbrev"]].copy()

partyMap = {
    100: "Democrat",
    200: "Republican",
}

members["party"] = members["party_code"].map(partyMap).fillna("Other")

memberLookup = members.set_index("icpsr").to_dict(orient="index")

for senator in gPositive.nodes():
    if senator in memberLookup:
        for key, value in memberLookup[senator].items():
            gPositive.nodes[senator][key] = value

nodes_df = members[members["icpsr"].isin(senators)].copy()
nodes_df = nodes_df[["icpsr", "bioname", "party", "state_abbrev"]].copy()

nodes_df.to_csv("S107_nodes.csv", index=False)
edges_df.to_csv("S107_edges.csv", index=False)

