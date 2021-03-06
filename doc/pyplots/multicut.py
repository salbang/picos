import picos as pic
import networkx as nx

#number of nodes
N=20

#Generate a graph with LCF notation (you can change the values below to obtain another graph!)
#We use this deterministic generator in order to have a constant inuput for doctest.
G=nx.LCF_graph(N,[1,3,14],5)
G=nx.DiGraph(G) #edges are bidirected

#generate edge capacities
c={}
for i,e in enumerate(G.edges()):
        c[e]=((-2)**i)%17 #an arbitrary sequence of numbers

#---------------#
#   multi cut   #
#---------------#

multicut=pic.Problem()

#pairs to be separated
pairs=[(0,12),(1,5),(1,19),(2,11),(3,4),(3,9),(3,18),(6,15),(10,14)]

#source and sink nodes
s=16
t=10

#convert the capacities as a picos expression
cc=pic.new_param('c',c)

#list of sources
sources=set([p[0] for p in pairs])


#cut variable
y={}
for e in G.edges():
        y[e]=multicut.add_variable('y[{0}]'.format(e),1,vtype='binary')

#potentials (one for each source)
p={}
for s in sources:
        p[s]=multicut.add_variable('p[{0}]'.format(s),N)

#potential inequalities
multicut.add_list_of_constraints(
        [y[i,j]>p[s][i]-p[s][j]
        for s in sources
        for (i,j) in G.edges()],        #list of constraints
        ['i','j','s'],'edges x sources')#indices and set they belong to

#one-potentials at source
multicut.add_list_of_constraints(
        [p[s][s]==1 for s in sources],
        's','sources')

#zero-potentials at sink
multicut.add_list_of_constraints(
        [p[s][t]==0 for (s,t) in pairs],
        ['s','t'],'pairs')

#nonnegativity
multicut.add_list_of_constraints(
        [p[s]>0 for s in sources],
        's','sources')

#objective
multicut.set_objective('min',
                pic.sum([cc[e]*y[e] for e in G.edges()],
                        [('e',2)],'edges')
                )
                
#print multicut
multicut.solve(verbose=0)


#print 'The minimal multicut has capacity {0}'.format(multicut.obj_value())

cut=[e for e in G.edges() if y[e].value[0]==1]

#display the cut
import pylab

fig=pylab.figure(figsize=(11,8))

#a Layout for which the graph is planar (or use pos=nx.spring_layout(G) with another graph)
pos={
 0: (0.07, 0.7),
 1: (0.18, 0.78),
 2: (0.26, 0.45),
 3: (0.27, 0.66),
 4: (0.42, 0.79),
 5: (0.56, 0.95),
 6: (0.6,  0.8),
 7: (0.64, 0.65),
 8: (0.55, 0.37),
 9: (0.65, 0.3),
 10:(0.77, 0.46),
 11:(0.83, 0.66),
 12:(0.90, 0.41),
 13:(0.70, 0.1),
 14:(0.56, 0.16),
 15:(0.40, 0.17),
 16:(0.28, 0.05),
 17:(0.03, 0.38),
 18:(0.01, 0.66),
 19: (0, 0.95)}

#pairs of dark and light colors
colors=[('Yellow','#FFFFE0'),
        ('#888888','#DDDDDD'),
        ('Dodgerblue','Aqua'),
        ('DarkGreen','GreenYellow'),
        ('DarkViolet','Violet'),
        ('SaddleBrown','Peru'),
        ('Red','Tomato'),
        ('DarkGoldenRod','Gold'),
        ]
        
node_colors=['w']*N
for i,s in enumerate(sources):
        node_colors[s]=colors[i][0]
        for t in [t for (s0,t) in pairs if s0==s]:
                node_colors[t]=colors[i][1]

nx.draw_networkx(G,pos,
                edgelist=[e for e in G.edges() if e not in cut],
                node_color=node_colors)

nx.draw_networkx_edges(G,pos,
                edgelist=cut,
                edge_color='r')

#hide axis
fig.gca().axes.get_xaxis().set_ticks([])
fig.gca().axes.get_yaxis().set_ticks([])

pylab.show()
