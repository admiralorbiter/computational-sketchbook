"""
Basic AI behaviors for kids.

Implements simple decision-making logic for house selection,
trick-or-treating, and basic movement patterns.
"""

import random
from typing import List, Optional
from ..entities.kid import Kid, KidState
from ..entities.house import House
from ..utils.vector2 import Vector2


class BasicBehaviors:
    """
    Basic AI behaviors for kids.
    
    Implements simple decision-making without complex pathfinding.
    """
    
    @staticmethod
    def select_house(kid: Kid, world) -> Optional[House]:
        """
        Select a house for trick-or-treating.
        
        Args:
            kid: Kid entity making the decision
            world: GameWorld instance
            
        Returns:
            Selected house or None if no valid houses
        """
        if not world.houses:
            return None
        
        # Filter out houses on cooldown
        available_houses = [house for house in world.houses if house.is_available()]
        
        if not available_houses:
            return None
        
        # Filter out cursed houses (kids avoid them)
        preferred_houses = [h for h in available_houses if not h.is_cursed()]
        
        # If all houses are cursed, pick least cursed or wait
        if not preferred_houses:
            preferred_houses = available_houses
        
        # Prefer blessed houses (higher weight)
        blessed_houses = [h for h in preferred_houses if h.is_blessed()]
        if blessed_houses and random.random() < 0.7:  # 70% chance to prefer blessed
            return random.choice(blessed_houses)
        
        return random.choice(preferred_houses)
    
    @staticmethod
    def should_visit_house(kid: Kid, house: House) -> bool:
        """
        Determine if kid should visit a specific house.
        
        Args:
            kid: Kid entity
            house: House to consider
            
        Returns:
            True if kid should visit this house
        """
        # For now, always visit houses
        # Later this could consider:
        # - Distance to house
        # - House quality
        # - Kid's mood and preferences
        # - Whether house is cursed/blessed
        return True
    
    @staticmethod
    def calculate_house_attraction(kid: Kid, house: House) -> float:
        """
        Calculate how attractive a house is to a kid.
        
        Args:
            kid: Kid entity
            house: House to evaluate
            
        Returns:
            Attraction score (0.0 to 1.0)
        """
        # Base attraction from house
        base_attraction = house.get_attraction_strength(kid.position)
        
        # Modify based on kid's personality
        personality_modifier = BasicBehaviors._get_personality_house_preference(kid, house)
        
        # Modify based on distance (closer is better)
        distance = kid.position.distance_to(house.position)
        max_distance = 500.0  # Maximum distance to consider
        distance_factor = max(0.0, 1.0 - (distance / max_distance))
        
        # Combine factors
        final_attraction = base_attraction * personality_modifier * distance_factor
        
        return min(1.0, final_attraction)
    
    @staticmethod
    def _get_personality_house_preference(kid: Kid, house: House) -> float:
        """Get house preference modifier based on kid's personality."""
        # High-quality houses are more attractive to certain personalities
        if kid.personality.name == "VALUE_INVESTOR":
            # Value investors prefer high-quality houses
            return 0.5 + (house.quality * 0.2)
        elif kid.personality.name == "HOARDER":
            # Hoarders prefer any house that gives candy
            return 1.0
        elif kid.personality.name == "SOCIAL_TRADER":
            # Social traders prefer houses where other kids are
            # (simplified: prefer mid-quality houses)
            return 0.8 if house.quality == 2 else 1.0
        else:
            # Default: slight preference for higher quality
            return 0.7 + (house.quality * 0.1)
    
    @staticmethod
    def execute_trick_or_treat(kid: Kid, house: House, renderer=None) -> bool:
        """
        Execute trick-or-treating at a house.
        
        Args:
            kid: Kid entity
            house: House being visited
            renderer: Optional renderer for particle effects
            
        Returns:
            True if successful, False otherwise
        """
        if not house.can_dispense_candy():
            return False
        
        # Get candy from house
        candy_given = house.dispense_candy()
        
        if not candy_given:
            return False
        
        # Add candy to kid's inventory
        for candy_type, quantity in candy_given.items():
            kid.add_candy(candy_type, quantity)
        
        # Emit particles for visual feedback
        if renderer:
            # Use the first candy type for particle color
            first_candy_type = list(candy_given.keys())[0] if candy_given else "chocolate"
            renderer.emit_candy_particles(house.position, first_candy_type)
        
        # Update kid's mood based on candy received
        BasicBehaviors._update_mood_from_candy(kid, candy_given)
        
        return True
    
    @staticmethod
    def _update_mood_from_candy(kid: Kid, candy_received: dict):
        """Update kid's mood based on candy received."""
        if not candy_received:
            return
        
        # Count total candy pieces
        total_candy = sum(candy_received.values())
        
        # Update mood based on amount and quality
        if total_candy >= 3:
            # Lots of candy - make kid happy
            if kid.mood.name != "HAPPY":
                kid.mood = kid.mood.__class__.HAPPY
        elif total_candy == 1:
            # Little candy - might make kid anxious
            if kid.mood.name == "NEUTRAL":
                kid.mood = kid.mood.__class__.ANXIOUS
        # Otherwise, keep current mood
    
    @staticmethod
    def should_seek_new_house(kid: Kid) -> bool:
        """
        Determine if kid should seek a new house.
        
        Args:
            kid: Kid entity
            
        Returns:
            True if kid should seek a new house
        """
        # Simple logic: if idle for a while, seek a house
        if kid.state == KidState.IDLE:
            # 70% chance to seek house when idle
            return random.random() < 0.7
        
        # If trick-or-treating is done, seek new house
        if kid.state == KidState.TRICK_OR_TREATING and kid.trick_or_treat_timer <= 0:
            return True
        
        return False
    
    @staticmethod
    def get_movement_target(kid: Kid, world) -> Optional[Vector2]:
        """
        Get the target position for kid movement.
        
        Args:
            kid: Kid entity
            world: GameWorld instance
            
        Returns:
            Target position or None
        """
        if kid.state == KidState.MOVING_TO_HOUSE and kid.target_position:
            return kid.target_position
        
        if kid.state == KidState.SEEKING_TRADE:
            # For now, just pick a random position
            # Later this could be toward other kids
            world_width = 2000  # Get from config
            world_height = 2000
            x = random.uniform(100, world_width - 100)
            y = random.uniform(100, world_height - 100)
            return Vector2(x, y)
        
        return None
    
    @staticmethod
    def update_kid_behavior(kid: Kid, world, dt: float):
        """
        Update a kid's behavior based on current state.
        
        Args:
            kid: Kid entity to update
            world: GameWorld instance
            dt: Delta time
        """
        if kid.state == KidState.IDLE:
            # Decide whether to trade or visit house
            if BasicBehaviors.should_seek_trade(kid, world):
                kid.state = KidState.SEEKING_TRADE
            elif BasicBehaviors.should_seek_new_house(kid):
                house = BasicBehaviors.select_house(kid, world)
                if house and BasicBehaviors.should_visit_house(kid, house):
                    kid.target_house = house
                    kid.target_position = house.position
                    kid.state = KidState.MOVING_TO_HOUSE
                    
                    # Try to find a path using pathfinding
                    if world.pathfinding_manager and kid.use_pathfinding:
                        path = world.pathfinding_manager.find_path(kid.position, house.position)
                        if path:
                            kid.set_path(path)
                        else:
                            # No path found, clear path to use direct movement
                            kid.clear_path()
        
        elif kid.state == KidState.MOVING_TO_HOUSE:
            if kid.reached_target() and kid.target_house:
                # Arrived at house, start trick-or-treating
                kid.state = KidState.TRICK_OR_TREATING
                kid.trick_or_treat_timer = 2.0  # Spend 2 seconds at house
                kid.clear_path()  # Clear path when arriving
        
        elif kid.state == KidState.TRICK_OR_TREATING:
            if kid.trick_or_treat_timer <= 0:
                # Done trick-or-treating, go back to idle
                kid.state = KidState.IDLE
                kid.target_house = None
                kid.target_position = None
                kid.clear_path()
        
        elif kid.state == KidState.SEEKING_TRADE:
            # Try to find trading partners and make trades
            BasicBehaviors.attempt_trade(kid, world)
    
    @staticmethod
    def should_seek_trade(kid: Kid, world) -> bool:
        """
        Determine if kid should seek a trade.
        
        Args:
            kid: Kid entity
            world: GameWorld instance
            
        Returns:
            True if kid should seek a trade
        """
        # Must have candy to trade
        if not kid.inventory:
            return False
        
        # Check cooldown
        if kid.trade_cooldown > 0:
            return False
        
        # Must have at least 2 pieces of candy to consider trading
        total_candy = sum(kid.inventory.values())
        if total_candy < 2:
            return False
        
        # Probability based on personality
        trade_probability = {
            "VALUE_INVESTOR": 0.4,    # Moderate
            "MOMENTUM_TRADER": 0.7,   # High
            "HOARDER": 0.1,           # Very low
            "SOCIAL_TRADER": 0.8,     # Very high
            "PANIC_SELLER": 0.6,      # High
        }
        
        personality_name = kid.personality.name
        base_prob = trade_probability.get(personality_name, 0.5)
        
        # Mood modifier
        if kid.mood.name == "HAPPY":
            base_prob *= 1.2
        elif kid.mood.name == "ANXIOUS":
            base_prob *= 1.5  # Anxious kids trade more
        elif kid.mood.name == "PANIC":
            base_prob *= 2.0  # Panic sellers trade a lot
        
        return random.random() < min(1.0, base_prob)
    
    @staticmethod
    def attempt_trade(kid: Kid, world):
        """
        Attempt to find a trading partner and execute a trade.
        
        Args:
            kid: Kid entity seeking to trade
            world: GameWorld instance
        """
        # Get nearby kids from spatial grid
        nearby_kids = world.spatial_grid.get_nearby(kid.position, 150.0)
        
        # Filter to valid trading partners
        valid_partners = []
        for other_kid in nearby_kids:
            if not isinstance(other_kid, Kid):
                continue
            if other_kid == kid:
                continue
            if not other_kid.active:
                continue
            if other_kid.state == KidState.IN_TRADE:
                continue  # Don't interrupt ongoing trades
            if not other_kid.inventory:
                continue  # Must have candy
            valid_partners.append(other_kid)
        
        if not valid_partners:
            kid.state = KidState.IDLE
            return
        
        # Pick a random partner
        partner = random.choice(valid_partners)
        
        # Generate a simple 1-for-1 trade proposal
        trade_offer, trade_request = BasicBehaviors._generate_trade_proposal(kid, partner)
        
        if not trade_offer or not trade_request:
            kid.state = KidState.IDLE
            return
        
        # Evaluate the trade from partner's perspective
        if world.economy:
            partner_score = partner.evaluate_trade(trade_offer, trade_request, world.economy)
            
            # If partner accepts, execute the trade
            if partner_score > 0:
                BasicBehaviors._execute_trade(kid, partner, trade_offer, trade_request, world)
                kid.trade_cooldown = 3.0  # 3 second cooldown
        
        kid.state = KidState.IDLE
    
    @staticmethod
    def _generate_trade_proposal(kid: Kid, partner: Kid):
        """
        Generate a trade proposal (1-for-1 or multi-item based on settings).
        
        Args:
            kid: Kid making the proposal
            partner: Potential trading partner
            
        Returns:
            Tuple of (offer_dict, request_dict) or (None, None) if can't propose
        """
        # Check if multi-item trades are enabled
        multi_item_enabled = True  # Default to enabled
        if hasattr(kid, 'world') and kid.world and kid.world.economy:
            multi_item_enabled = kid.world.economy.settings.get('enable_multi_item_trades', True)
        
        if multi_item_enabled and random.random() < 0.3:  # 30% chance for multi-item
            return BasicBehaviors._generate_multi_item_proposal(kid, partner)
        else:
            return BasicBehaviors._generate_single_item_proposal(kid, partner)
    
    @staticmethod
    def _generate_single_item_proposal(kid: Kid, partner: Kid):
        """Generate a simple 1-for-1 trade proposal."""
        # Pick a candy we have to offer
        available_to_give = [(candy, qty) for candy, qty in kid.inventory.items() if qty > 0]
        if not available_to_give:
            return None, None
        
        offer_candy, offer_qty = random.choice(available_to_give)
        offer = {offer_candy: 1}
        
        # Pick a candy the partner has that we want
        partner_candies = [(candy, qty) for candy, qty in partner.inventory.items() if qty > 0]
        if not partner_candies:
            return None, None
        
        # Score potential requests based on our preferences
        scored_requests = []
        for candy, qty in partner_candies:
            preference = kid.preferences.get(candy, 0.5)
            we_have = kid.inventory.get(candy, 0)
            # Want candy we prefer and don't have much of
            score = preference * (1.0 if we_have == 0 else 0.5)
            scored_requests.append((candy, score))
        
        # Pick highest scored request
        if scored_requests:
            request_candy = max(scored_requests, key=lambda x: x[1])[0]
            request = {request_candy: 1}
        else:
            # Fallback: just pick any candy
            request_candy, _ = random.choice(partner_candies)
            request = {request_candy: 1}
        
        return offer, request
    
    @staticmethod
    def _generate_multi_item_proposal(kid: Kid, partner: Kid):
        """Generate a multi-item trade proposal."""
        # Pick 1-3 candies we have to offer
        available_to_give = [(candy, qty) for candy, qty in kid.inventory.items() if qty > 0]
        if not available_to_give:
            return None, None
        
        num_offer_items = min(random.randint(1, 3), len(available_to_give))
        offer_items = random.sample(available_to_give, num_offer_items)
        
        offer = {}
        for candy, qty in offer_items:
            # Offer 1-2 pieces of each candy
            offer_qty = min(random.randint(1, 2), qty)
            offer[candy] = offer_qty
        
        # Pick 1-3 candies the partner has that we want
        partner_candies = [(candy, qty) for candy, qty in partner.inventory.items() if qty > 0]
        if not partner_candies:
            return None, None
        
        num_request_items = min(random.randint(1, 3), len(partner_candies))
        request_items = random.sample(partner_candies, num_request_items)
        
        request = {}
        for candy, qty in request_items:
            # Request 1-2 pieces of each candy
            request_qty = min(random.randint(1, 2), qty)
            request[candy] = request_qty
        
        return offer, request
    
    @staticmethod
    def _execute_trade(kid: Kid, partner: Kid, offer: dict, request: dict, world):
        """
        Execute a trade between two kids.
        
        Args:
            kid: First kid (proposer)
            partner: Second kid (accepter)
            offer: What kid is offering
            request: What kid is requesting
            world: GameWorld instance
        """
        # Verify both kids have the required candy
        for candy_type, quantity in offer.items():
            if not kid.has_candy(candy_type, quantity):
                return  # Can't execute, kid doesn't have the candy
        
        for candy_type, quantity in request.items():
            if not partner.has_candy(candy_type, quantity):
                return  # Can't execute, partner doesn't have the candy
        
        # Execute the swap
        for candy_type, quantity in offer.items():
            kid.remove_candy(candy_type, quantity)
            partner.add_candy(candy_type, quantity)
        
        for candy_type, quantity in request.items():
            partner.remove_candy(candy_type, quantity)
            kid.add_candy(candy_type, quantity)
        
        # Record trade in economy
        if world.economy:
            # Simple price calculation: quantity of offer candy
            for candy_type in offer.keys():
                world.economy.record_trade(candy_type, 1.0, kid.id, partner.id)
        
        # Update beliefs from trade (price discovery)
        if hasattr(kid, 'update_beliefs_from_trade') and world.economy:
            learning_rate = world.economy.settings.get('convergence_rate', 0.1)
            kid.update_beliefs_from_trade(offer, request, world.economy, learning_rate)
            partner.update_beliefs_from_trade(request, offer, world.economy, learning_rate)
        
        # Visual effects for trade
        BasicBehaviors._emit_trade_effects(kid, partner, offer, request, world)
        
        # Record in kid's recent trades
        kid.recent_trades.append({
            "partner": partner.id,
            "offer": offer.copy(),
            "request": request.copy()
        })
        partner.recent_trades.append({
            "partner": kid.id,
            "offer": request.copy(),  # From partner's perspective
            "request": offer.copy()
        })
        
        # Keep only last 10 trades
        if len(kid.recent_trades) > 10:
            kid.recent_trades.pop(0)
        if len(partner.recent_trades) > 10:
            partner.recent_trades.pop(0)
        
        print(f"Trade: {kid.id} <-> {partner.id}")
    
    @staticmethod
    def _emit_trade_effects(kid: Kid, partner: Kid, offer: dict, request: dict, world):
        """Emit visual effects for a completed trade."""
        # Get renderer from world (if available)
        renderer = getattr(world, 'renderer', None)
        if not renderer:
            return
        
        # Emit particle effects
        if hasattr(renderer, 'particle_system'):
            # Trade particles between kids
            renderer.particle_system.emit_trade_particles(
                kid.position, partner.position, offer, request
            )
            
            # Success particles at midpoint
            mid_point = Vector2(
                (kid.position.x + partner.position.x) / 2,
                (kid.position.y + partner.position.y) / 2
            )
            renderer.particle_system.emit_trade_success_particles(mid_point)
        
        # Emit floating text
        if hasattr(renderer, 'floating_text_system'):
            mid_point = Vector2(
                (kid.position.x + partner.position.x) / 2,
                (kid.position.y + partner.position.y) / 2
            )
            renderer.floating_text_system.add_trade_text(mid_point, offer, request)
