from ai_dungeon import config
from ai_dungeon.storage.user_info import UserInfo
from gql import gql, Client, WebsocketsTransport


async def _execute_query(query, variables=None, **init_payload):
    """
    Handful wrapper to execute queries
    :param query: GraphQL query as plain text
    :param variables: Variables to insert
    :param init_payload: Payload to send while initializing connection
    :return: Query result
    """
    transport = WebsocketsTransport(url=config.WS_URL, init_payload=init_payload)

    async with Client(
            transport=transport,
    ) as session:
        return await session.execute(gql(query), variable_values=variables or {})


async def create_account() -> str:
    """
    :return: Anonymous token
    """
    q = """
    mutation {
        createAnonymousAccount {
            accessToken
        }
    }
    """
    return (await _execute_query(q))['createAnonymousAccount']['accessToken']


async def retrieve_scenario(user_info: UserInfo, scenario='scenario:458612'):
    """
    By default returns initial scenario
    :param user_info: Info About user. Should contain token
    :param scenario: Scenario formatted as "scenario:<id>"
    :return: Info about scenario using format below
    """
    q = """
    query ($id: String) { 
        content(id: $id) {
            id
            prompt
            error
            options {
                id
                title
            }
        }
    } 
    """
    results = await _execute_query(q, variables={'id': scenario}, token=UserInfo.token)
    return results['content']


async def create_adventure_from_scenario(user_info: UserInfo, scenario):
    """

    :param user_info: Info About User. Should contain token.
    :param scenario: Scenario in formatted as "scenario:<id>"
    :return: Adventure id formatted as "adventure:<id>"
    """
    q = """
        mutation ($id: String, $prompt: String) {
            createAdventureFromScenarioId(id: $id, prompt: $prompt) {
                id 
            }
        } 
    """
    results = await _execute_query(q, variables={
        'id': scenario,
        'prompt': user_info.prompt
    }, token=user_info.token)

    return results['createAdventureFromScenarioId']['id']


async def get_adventure_info(user_info: UserInfo, adventure):
    """

    :param user_info: Info about user. Should contain token.
    :param adventure: Adventure formatted as "adventure:<id>"
    :return: Info about adventure using format below
    """
    q = """
        query ($id: String, $playPublicId: String) {
            content(id: $id, playPublicId: $playPublicId) {
                id
                actions {
                    id
                    text
                }
            }
        }
    """
    results = await _execute_query(q, variables={
        'id': adventure
    }, token=user_info.token)

    return results['content']


async def adventure_send_action(user_info: UserInfo, inp):
    """
    :param user_info: Info about user. Should contain token.
    :param inp: Input in format { "type": "(do|say|story)", "text": str, "id": "adventure:<id>" }
    :return: Info about adventure using format below.
    """
    q = """
        mutation ($input: ContentActionInput) {
            sendAction(input: $input) {
                id
                died
                actions {
                    id
                    text
                }
            }
        } 
    """

    results = await _execute_query(q, variables={
        'input': inp
    }, token=user_info.token)

    return results['sendAction']
