
import sys
sys.path.append('.')

from backend.services import api_service

def test_detailed_player_data():
    print("🔍 Testing api_service.process_detailed_player_data()...")
    
    player_code = "TEKT#518"  # Use your actual player code
    filter_data = {
        'character': 'all',
        'opponent': 'all', 
        'opponent_character': 'all'
    }
    
    try:
        result = api_service.process_detailed_player_data(player_code, filter_data)
        
        print(f"🔍 Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"🔍 Result keys: {list(result.keys())}")
            print(f"🔍 Has character_stats: {'character_stats' in result}")
            print(f"🔍 Has date_stats: {'date_stats' in result}")
            print(f"🔍 Has filter_options: {'filter_options' in result}")
        else:
            print(f"🔍 Result value: {result}")
            
    except Exception as e:
        import traceback
        print(f"🔍 Exception: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_detailed_player_data()