"""
Module for dealing with experiment user data via proposal allocations API
"""

import logging
import os
from typing import List

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportError

from src.exceptions import ProposalAllocationsError

logger = logging.getLogger(__name__)

UOWS_API_KEY = os.environ.get("UOWS_API_KEY", "shh")
ALLOCATIONS_URL = os.environ.get("ALLOCATIONS_URL", "https://devapi.facilities.rl.ac.uk/proposal-allocations/graphql")


async def get_experiments_for_user_number(user_number: int) -> List[int]:
    """
    Return the experiment (RB) numbers related to the given user number
    :param user_number: The user number
    :return: A list of Experiment (RB) numbers
    """
    transport = AIOHTTPTransport(url=ALLOCATIONS_URL, headers={"Authorisation": f"token {UOWS_API_KEY}"})
    client = Client(transport=transport, fetch_schema_from_transport=True)
    logger.info("Fetching experiments for user number %s", user_number)
    query = gql(
        f"""
        {{
      proposals(
        filter: {{un: "{user_number}", facilities: ["ISIS"], includeWithdrawn: false}}
      ) {{
        referenceNumber
      }}
    }}
    """
    )
    try:
        response = await client.execute_async(query)
        return [int(proposal["referenceNumber"]) for proposal in response["proposals"]]
    except TransportError as e:
        logger.exception("Failed to query allocations API", exc_info=e)
        raise ProposalAllocationsError()
