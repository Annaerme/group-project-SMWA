"""
Utility functions for Mastodon data collection

This module provides helper functions to simplify common Mastodon API operations
including data collection with pagination and cleaning.
"""

import time
import pandas as pd
from bs4 import BeautifulSoup


def fetch_hashtag_toots(mastodon, hashtag, max_toots=200, delay=0.5, verbose=True):
    """
    Fetch toots by hashtag with automatic pagination.
    
    Parameters:
    -----------
    mastodon : Mastodon
        Authenticated Mastodon client instance
    hashtag : str
        Hashtag to search (without #)
    max_toots : int, default=200
        Maximum number of toots to retrieve
    delay : float, default=0.5
        Delay in seconds between API requests to avoid rate limiting
    verbose : bool, default=True
        Print progress messages
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the retrieved toots
    
    Example:
    --------
    >>> from mastodon import Mastodon
    >>> from mastodon_utils import fetch_hashtag_toots
    >>> 
    >>> mastodon = Mastodon(access_token='...', api_base_url='https://mastodon.social')
    >>> df = fetch_hashtag_toots(mastodon, "photography", max_toots=200)
    """
    if verbose:
        print(f"Fetching toots for #{hashtag}...\n")
    
    # Fetch first batch
    timeline = mastodon.timeline_hashtag(hashtag, limit=40)
    all_toots = list(timeline)
    
    if verbose:
        print(f"Batch 1: {len(all_toots)} toots")
    
    # Fetch additional batches
    pages_needed = (max_toots // 40) - 1
    
    for i in range(pages_needed):
        time.sleep(delay)
        
        timeline = mastodon.fetch_next(timeline)
        if timeline:
            all_toots.extend(timeline)
            if verbose:
                print(f"Batch {i+2}: {len(timeline)} toots (total: {len(all_toots)})")
        else:
            if verbose:
                print(f"Reached end of available data after {len(all_toots)} toots")
            break
    
    # Convert to DataFrame and limit to max_toots
    df = pd.DataFrame(all_toots[:max_toots])
    
    if verbose:
        print(f"\n✓ Total retrieved: {len(df)} toots")
    
    return df


def fetch_account_toots(mastodon, account_id, max_toots=400, delay=0.5, verbose=True):
    """
    Fetch toots from a specific account with automatic pagination.
    
    Parameters:
    -----------
    mastodon : Mastodon
        Authenticated Mastodon client instance
    account_id : str
        Account ID to fetch toots from
    max_toots : int, default=400
        Maximum number of toots to retrieve
    delay : float, default=0.5
        Delay in seconds between API requests
    verbose : bool, default=True
        Print progress messages
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing the retrieved toots
    """
    if verbose:
        print(f"Fetching toots from account {account_id}...")
    
    # Fetch first batch
    statuses = mastodon.account_statuses(account_id, limit=40)
    all_toots = list(statuses)
    
    # Fetch additional batches
    pages_needed = (max_toots // 40) - 1
    
    for i in range(pages_needed):
        time.sleep(delay)
        
        statuses = mastodon.fetch_next(statuses)
        if statuses:
            all_toots.extend(statuses)
        else:
            break
    
    # Convert to DataFrame and limit to max_toots
    df = pd.DataFrame(all_toots[:max_toots])
    
    if verbose:
        print(f"✓ Retrieved {len(df)} toots")
    
    return df


def clean_html(html_text):
    """
    Remove HTML tags from text using BeautifulSoup.
    
    Parameters:
    -----------
    html_text : str
        HTML-formatted text
    
    Returns:
    --------
    str
        Plain text with HTML tags removed
    
    Example:
    --------
    >>> clean_html('<p>Hello <strong>world</strong>!</p>')
    'Hello world!'
    """
    return BeautifulSoup(html_text, 'html.parser').get_text()


def add_clean_content(df):
    """
    Add a 'clean_content' column to the DataFrame by removing HTML tags.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing a 'content' column with HTML-formatted text
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'clean_content' column
    
    Example:
    --------
    >>> df = fetch_hashtag_toots(mastodon, "photography")
    >>> df = add_clean_content(df)
    >>> print(df['clean_content'].head())
    """
    df['clean_content'] = df['content'].apply(clean_html)
    return df


def add_instance_info(df, mastodon_api_base_url):
    """
    Add instance information to the DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing an 'account' column
    mastodon_api_base_url : str
        Base URL of the authenticated Mastodon instance
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'instance' column
    
    Example:
    --------
    >>> df = fetch_hashtag_toots(mastodon, "photography")
    >>> df = add_instance_info(df, mastodon.api_base_url)
    >>> print(df['instance'].value_counts().head())
    """
    df['instance'] = df['account'].apply(
        lambda x: x['acct'].split('@')[-1] if '@' in x['acct'] 
        else mastodon_api_base_url.replace('https://', '')
    )
    return df


def filter_by_language(df, language='en', verbose=True):
    """
    Filter toots by language.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing a 'language' column
    language : str, default='en'
        Language code to filter for (e.g., 'en', 'es', 'fr')
    verbose : bool, default=True
        Print filtering information
    
    Returns:
    --------
    pd.DataFrame
        DataFrame filtered to only include toots in the specified language
    
    Example:
    --------
    >>> df = fetch_hashtag_toots(mastodon, "photography", max_toots=200)
    >>> df_en = filter_by_language(df, language='en')
    >>> print(f"English toots: {len(df_en)}")
    """
    original_count = len(df)
    
    # Remove None values first
    df = df[df['language'].notna()]
    
    # Filter for specified language
    df = df[df['language'] == language].reset_index(drop=True)
    
    if verbose:
        print(f"Language filter ('{language}'):")
        print(f"  Before: {original_count} toots")
        print(f"  After: {len(df)} toots ({len(df)/original_count*100:.1f}%)")
    
    return df


def select_columns(df, columns=['text', 'created_at'], rename_content=True):
    """
    Select and optionally rename specific columns from the DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing toot data
    columns : list, default=['text', 'created_at']
        List of column names to keep
    rename_content : bool, default=True
        If True and 'text' is in columns, will look for 'clean_content' or 'content'
        and rename it to 'text'
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with only the specified columns
    
    Example:
    --------
    >>> df = fetch_hashtag_toots(mastodon, "photography")
    >>> df = add_clean_content(df)
    >>> df = select_columns(df, columns=['text', 'created_at'])
    """
    # Handle text column renaming
    if rename_content and 'text' in columns:
        if 'clean_content' in df.columns:
            df = df.rename(columns={'clean_content': 'text'})
        elif 'content' in df.columns:
            df = df.rename(columns={'content': 'text'})
    
    # Select only specified columns that exist
    available_columns = [col for col in columns if col in df.columns]
    
    return df[available_columns].reset_index(drop=True)


def print_data_quality_report(df):
    """
    Print a data quality report for the collected toots.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing toot data
    """
    print("DATA QUALITY REPORT:")
    print(f"  Total toots: {len(df)}")
    
    if 'id' in df.columns:
        unique_ids = df['id'].nunique()
        print(f"  Unique IDs: {unique_ids}")
        if unique_ids < len(df):
            print(f"  ⚠️  Warning: {len(df) - unique_ids} duplicate IDs")
    
    if 'reblog' in df.columns:
        retoots = df['reblog'].notna().sum()
        print(f"  Retoots/boosts: {retoots} ({retoots/len(df)*100:.1f}%)")
    
    if 'language' in df.columns:
        lang_counts = df['language'].value_counts()
        print(f"\n  Languages: {len(lang_counts)}")
        print(f"  Top 5 languages:")
        for lang, count in lang_counts.head(5).items():
            print(f"    • {lang}: {count} toots ({count/len(df)*100:.1f}%)")
    
    if 'instance' in df.columns:
        instance_counts = df['instance'].value_counts()
        print(f"\n  Toots from {len(instance_counts)} different instances")
        print(f"  Top 5 instances:")
        for instance, count in instance_counts.head(5).items():
            print(f"    • {instance}: {count} toots ({count/len(df)*100:.1f}%)")
