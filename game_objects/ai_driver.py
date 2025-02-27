import random

class AIDriver:
    @staticmethod
    def make_decision(car, obstacles, look_ahead=300):
        # Filter and sort relevant obstacles
        relevant_obstacles = []
        for obs in obstacles:
            distance = obs.y - car.y
            # Consider obstacles ahead and slightly behind
            if -50 < distance < look_ahead:
                # Consider all lanes for better awareness
                lane_diff = abs(obs.lane - car.lane)
                if lane_diff <= 1:  # Same or adjacent lanes
                    relevant_obstacles.append((obs, distance))
        
        # Sort by absolute distance for priority
        relevant_obstacles.sort(key=lambda x: abs(x[1]))
        
        # If no obstacles and not in middle lane, consider moving to middle
        if not relevant_obstacles:
            if car.lane != 1 and not car.is_changing_lanes and random.random() < 0.01:  # 1% chance to move to middle
                return -1 if car.lane > 1 else 1
            return None
            
        # Check for threats in current lane
        same_lane_threats = [
            (obs, dist) for obs, dist in relevant_obstacles 
            if obs.lane == car.lane and dist > 0  # Only forward threats
        ]
        
        if same_lane_threats:
            closest_threat, threat_dist = same_lane_threats[0]
            
            # Calculate safety scores for each lane
            lane_scores = {0: 100, 1: 100, 2: 100}  # Base scores
            
            # Reduce scores based on obstacles
            for obs, dist in relevant_obstacles:
                if dist > 0:  # Forward obstacles reduce score more
                    lane_scores[obs.lane] -= 100 / (dist / 50)
                else:  # Rear obstacles reduce score less
                    lane_scores[obs.lane] -= 50 / (abs(dist) / 50)
            
            # Bonus for current lane to reduce unnecessary changes
            lane_scores[car.lane] += 20
            
            # If immediate danger
            if threat_dist < 100:
                # Find best escape route
                possible_moves = []
                if car.lane > 0:  # Can move left
                    if lane_scores[car.lane - 1] > 50:  # Reasonable safety threshold
                        possible_moves.append(-1)
                if car.lane < 2:  # Can move right
                    if lane_scores[car.lane + 1] > 50:
                        possible_moves.append(1)
                
                if possible_moves:
                    # Choose lane with highest safety score
                    return max(possible_moves, 
                             key=lambda move: lane_scores[car.lane + move])
            
            # For medium-range threats, be more strategic
            elif threat_dist < 200:
                # Only change if significantly better option exists
                best_lane = max(range(3), 
                              key=lambda l: lane_scores[l] if abs(l - car.lane) <= 1 else -float('inf'))
                if best_lane != car.lane and lane_scores[best_lane] > lane_scores[car.lane] + 30:
                    return 1 if best_lane > car.lane else -1
        
        return None 