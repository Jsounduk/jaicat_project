# lib/nlg/Social_media_post.py

# lib/nlg/Social_media_post.py

import random

def generate_caption(tags, mood="neutral"):
    mood_phrases = {
        "happy": ["Feeling blessed ✨", "Just good vibes 💛", "Smiles all day 😄"],
        "flirty": ["Catch me if you can 😉", "Play nice or play with me 😘", "Too hot to handle 🔥"],
        "sad": ["In my feelings today 💭", "Soft and quiet vibes 🖤"],
        "neutral": ["Just me.", "No filter needed.", "This happened."]
    }

    tag_phrases = {
        "bike": ["#BikerLife", "#RideOrDie"],
        "lace": ["#LingerieGoals", "#LaceQueen"],
        "Jay": ["#SirSaidSo", "#HisMuse"],
        "Samantha": ["#ShyButBold", "#SweetAndSpicy"]
    }

    # Select mood phrase
    mood_list = mood_phrases.get(mood, mood_phrases["neutral"])
    line1 = random.choice(mood_list)

    # Match tags to hashtags
    hash_tags = []
    for tag in tags:
        if tag.lower() in tag_phrases:
            hash_tags.extend(tag_phrases[tag.lower()])

    return f"{line1}\n" + " ".join(set(hash_tags))


import random
import textwrap

class SocialMediaPostGenerator:
    def __init__(self):
        self.templates = [
            "Check out our latest blog post: {link} #blog #update",
            "We're excited to announce that {event} is happening! Join us! #event #announcement",
            "Have you seen our new product? {product_name} is now available! #newproduct #shopnow",
            "Don't miss out on our special offer: {offer} #discount #sale",
            "Join us for a live session on {date}. Learn more: {link} #live #webinar",
        ]

    def generate_post(self, context):
        """Generate a social media post based on the given context."""
        template = random.choice(self.templates)
        return template.format(**context)

    def format_post(self, post):
        """Format the post for readability."""
        wrapped_post = textwrap.fill(post, width=60)  # Wrap the text to a specified width
        return wrapped_post

    def analyze_post(self, post):
        """Analyze the post for sentiment and engagement."""
        # Placeholder for sentiment analysis logic
        # In a real implementation, you might integrate an NLP library to analyze the post
        return {
            "length": len(post.split()),
            "sentiment": "neutral",  # Replace with actual sentiment analysis
            "engagement_score": random.randint(1, 10)  # Placeholder for engagement score
        }

# Example usage
if __name__ == "__main__":
    generator = SocialMediaPostGenerator()
    
    context = {
        "link": "https://example.com/blog",
        "event": "our annual conference",
        "product_name": "Amazing Gadget",
        "offer": "20% off on all items",
        "date": "October 15, 2024"
    }
    
    post = generator.generate_post(context)
    formatted_post = generator.format_post(post)
    
    print("Generated Post:")
    print(formatted_post)
    
    analysis = generator.analyze_post(formatted_post)
    print("\nPost Analysis:")
    print(analysis)
