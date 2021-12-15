from ai_dungeon import config
from ai_dungeon.storage.user_info import UserInfo
from gql import gql, Client, WebsocketsTransport, AIOHTTPTransport


async def _execute_http(query, variables=None, token=None):
    """
    Handful wrapper to execute queries via HTTP
    :param query: GraphQL query as plain text
    :param variables: Variables to insert
    :param token: Auth token
    :return: Query result
    """
    transport = AIOHTTPTransport(url=config.HTTP_URL, headers={
        "X-Access-Token": token
    } if token else None)

    async with Client(
            transport=transport,
    ) as session:
        return await session.execute(gql(query), variable_values=variables or {})


async def _execute_ws(query, variables=None, **init_payload):
    """
    Handful wrapper to execute queries via WS
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
    token = (await _execute_http(q))['createAnonymousAccount']['accessToken']

    q = """
    {
      user {
        id
        rewardAvailable
        isCurrentUser
        isAlpha
        isDeveloper
        icon
        avatar
        username
        hasPremium
        hasDragon
        shouldPromptReview
        isBannedFromOai
        blockedUsers
        acceptCommunityGuidelines
        verifiedAt
        gameSettings {
          id
          displayTheme
          displayColors
          commandList
          alignCommands
          defaultMode
          showModes
          textFont
          textSize
          textSpeed
          showFeedback
          showIconText
          playNarration
          enableBeta
          enableAlpha
          narrationVolume
          nsfwGeneration
          playMusic
          musicVolume
          webActionWindowSize
          mobileActionWindowSize
          displayScreen
          isFullScreen
          showCommands
          showCommands
          searchfilterPublished
          searchfilterSafe
          searchfilterFollowing
          __typename
        }
        continueAdventure {
          id
          publicId
          __typename
        }
        __typename
      }
    }
    """
    await _execute_http(q, token=token)

    q = """
    mutation ($input: EventInput) {
      sendEvent(input: $input)
    }
    """
    await _execute_http(q, variables={
        'input': {
            "eventName": "funnel_create_anonymous_user",
            "platform": "web"
        }
    }, token=token)

    return token


async def retrieve_scenario(user_info: UserInfo, scenario='edd5fdc0-9c81-11ea-a76c-177e6c0711b5'):
    """
    By default returns initial scenario
    :param user_info: Info About user. Should contain token
    :param scenario: Scenario formatted as "scenario:<id>"
    :return: Info about scenario using format below
    """
    q = """
    query ($publicId: String) {
      scenario(publicId: $publicId) {
        memory
        ...SelectOptionScenario
        __typename
      }
    }
    
    fragment SelectOptionScenario on Scenario {
      id
      prompt
      publicId
      options {
        id
        publicId
        title
        __typename
      }
      __typename
    }
    """
    results = await _execute_http(q, variables={'publicId': scenario}, token=user_info.token)
    return results['scenario']


async def create_adventure_from_scenario(user_info: UserInfo, scenario):
    """

    :param user_info: Info About User. Should contain token.
    :param scenario: Scenario in formatted as "scenario:<id>"
    :return: Adventure id formatted as "adventure:<id>"
    """
    q = """
        mutation ($scenarioId: String, $prompt: String, $memory: String) {
          addAdventure(scenarioId: $scenarioId, prompt: $prompt, memory: $memory) {
            id
            publicId
            title
            description
            musicTheme
            tags
            nsfw
            published
            createdAt
            updatedAt
            deletedAt
            publicId
            __typename
          }
        }
    """
    results = await _execute_http(q, variables={
        'scenarioId': scenario['id'],
        'prompt': user_info.prompt,
        'memory': scenario['memory']
    }, token=user_info.token)

    return results['addAdventure']['publicId']


async def get_adventure_info(user_info: UserInfo, adventure):
    """

    :param user_info: Info about user. Should contain token.
    :param adventure: Adventure public id
    :return: Info about adventure using format below
    """
    q = """
        query ($publicId: String, $limit: Int, $desc: Boolean) {
          adventure(publicId: $publicId) {
            id
            isOwner
            userJoined
            safeMode
            thirdPerson
            music
            events
            enableSummarization
            gameState
            actionCount
            actionWindow(limit: $limit, desc: $desc) {
              id
              text
              type
              decisionId
              imageUrl
              undoneAt
              deletedAt
              __typename
            }
            undoneWindow {
              ...ActionSubscriptionAction
              __typename
            }
            __typename
          }
        }
        
        fragment ActionSubscriptionAction on Action {
          id
          text
          type
          adventureId
          decisionId
          undoneAt
          deletedAt
          createdAt
          __typename
        }

    """
    results = await _execute_http(q, variables={
        'publicId': adventure,
        'limit': 500,
        'desc': True
    }, token=user_info.token)

    return results['adventure']


async def adventure_send_action(user_info: UserInfo, inp):
    """
    :param user_info: Info about user. Should contain token.
    :param inp: Input in format { "type": "(do|say|story)", "text": str, "id": "adventure:<id>" }
    :return: Info about adventure using format below.
    """
    q = """
        mutation ($input: ActionInput) {
          addAction(input: $input) {
            message
            time
            hasBannedWord
            returnedInput
            __typename
          }
        }
    """

    results = await _execute_http(q, variables={
        'input': inp
    }, token=user_info.token)

    return results['addAction']
