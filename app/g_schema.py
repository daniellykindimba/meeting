import graphene
import pendulum
from app.mutations import Mutation as AppMutation
from app.schemas import Query as AppQuery



QUERIES = (
    AppQuery,
)

MUTATIONS = (
    AppMutation,
)

SUBSCRIPTIONS = (
)




class AllQuery(*QUERIES):
    pass


class Mutation(*MUTATIONS):
    pass


class Subscription(*SUBSCRIPTIONS):
    pass



schema = graphene.Schema(query=AllQuery,
                         mutation=Mutation,
                        #  subscription=Subscription
                         )
