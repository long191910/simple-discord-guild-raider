import requests
import json
import random
import time
import threading
from colorama import Fore, init

init()

def load_tokens():
    with open('tk.txt', 'r') as f:
        return f.read().splitlines()

class DiscordSpammer:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.api_url = 'https://canary.discord.com/api/v9'

    def get_channels(self, guild_id):
        try:
            r = requests.get(f'{self.api_url}/guilds/{guild_id}/channels', headers=self.headers)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"{Fore.RED}[-] Error getting channels: {r.status_code}")
                return []
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}")
            return []

    def check_channel_permissions(self, channel_id):
        try:
            payload = {'content': 'antigore'}
            r = requests.post(f'{self.api_url}/channels/{channel_id}/messages', 
                            headers=self.headers, 
                            data=json.dumps(payload))
            if r.status_code == 200:
                message_id = r.json()['id']
                requests.delete(f'{self.api_url}/channels/{channel_id}/messages/{message_id}', 
                              headers=self.headers)
                return True
            return False
        except:
            return False

    def send_message(self, channel_id, content):
        payload = {'content': content}
        r = requests.post(f'{self.api_url}/channels/{channel_id}/messages', 
                         headers=self.headers, 
                         data=json.dumps(payload))
        return r.status_code

    def check_token(self):
        try:
            r = requests.get(f'{self.api_url}/users/@me', headers=self.headers)
            if r.status_code == 200:
                return True
            return False
        except:
            return False

    def check_guild_access(self, guild_id):
        try:
            r = requests.get(f'{self.api_url}/guilds/{guild_id}', headers=self.headers)
            if r.status_code == 200:
                return True
            return False
        except:
            return False

    def spam_channels(self, guild_id, delay, msg_per_channel, message_content):
        try:
            if not self.check_token():
                print(f"{Fore.RED}[-] Invalid token: {self.token[:20]}...")
                return
            if not self.check_guild_access(guild_id):
                print(f"{Fore.RED}[-] No access to guild {guild_id}. Make sure the bot is in the server.")
                return

            channels = self.get_channels(guild_id)
            if not channels:
                print(f"{Fore.RED}[-] Could not get channels for guild {guild_id}")
                return
                
            print(f"{Fore.GREEN}[+] Connected with token: {self.token[:20]}...")
            
            for channel in channels:
                try:
                    if channel.get('type') == 0:  
                        if self.check_channel_permissions(channel.get('id')):
                            print(f"{Fore.CYAN}[+] Found writable channel: {channel.get('name')}")
                            messages_sent = 0
                            
                            while messages_sent < msg_per_channel:
                                random_prefix = "".join(random.choice("*#@!_$-") for _ in range(10))
                                random_suffix = "".join(random.choice("0123456789") for _ in range(10))
                                message = f"{random_prefix}\n{message_content} | {random_suffix}"
                                status = self.send_message(channel.get('id'), message)
                                
                                if status == 200:
                                    messages_sent += 1
                                    print(f"{Fore.CYAN}[+] Message sent in {channel.get('name')} ({messages_sent}/{msg_per_channel})")
                                else:
                                    print(f"{Fore.RED}[-] Failed to send in {channel.get('name')}")
                                
                                time.sleep(delay)
                        else:
                            print(f"{Fore.YELLOW}[!] No permission in channel: {channel.get('name')}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error processing channel: {str(e)}")
                    continue
                        
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}")

def start_spammer(token, guild_id, delay, msg_per_channel, message_content):
    spammer = DiscordSpammer(token)
    spammer.spam_channels(guild_id, delay, msg_per_channel, message_content)

if __name__ == "__main__":
    print(f"{Fore.CYAN}=== Tây Ninh Raider ===")
    print(f"{Fore.YELLOW}[!] Make sure:")
    print("1. The tokens in tk.txt are valid")
    print("2. The bots are invited to the target server")
    print("3. The Guild ID is correct")
    print("-------------------")
    
    guild_id = input("Enter Guild ID: ")
    delay = float(input("Enter delay between messages (seconds): "))
    msg_per_channel = int(input("Enter number of messages per channel: "))
    message_content = input("Enter message content: ")
    
    tokens = load_tokens()
    if not tokens:
        print(f"{Fore.RED}[-] No tokens found in tk.txt")
        exit()
        
    print(f"{Fore.CYAN}[+] Loaded {len(tokens)} tokens")
    threads = []
    
    for token in tokens:
        thread = threading.Thread(target=start_spammer, args=(token, guild_id, delay, msg_per_channel, message_content))
        thread.start()
        threads.append(thread)
        time.sleep(0.5)  

    for thread in threads:
        thread.join()
