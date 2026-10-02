class_name BuildManager
extends Node
## Manages building deployables during the preparation phase.

signal item_placed(deployable: Deployable, position: Vector2)
signal item_removed(deployable: Deployable, position: Vector2)
signal budget_changed(new_budget: int)

var budget_remaining: int = 0
var placed_items: Array[Dictionary] = [] # Array of {"deployable": Deployable, "position": Vector2}
var grid_size: int = 32

## Initializes the build manager with a starting budget.
func initialize(starting_budget: int) -> void:
	budget_remaining = starting_budget
	budget_changed.emit(budget_remaining)

## Checks if a deployable can be placed at the given grid-aligned position.
func can_place(deployable: Deployable, position: Vector2) -> bool:
	if budget_remaining < deployable.cost:
		return false
		
	# Check for collisions with other items
	var snapped_pos: Vector2 = position.snapped(Vector2(grid_size, grid_size))
	for item in placed_items:
		if item.position == snapped_pos:
			return false
			
	return true

## Places a deployable at the given position and deducts cost.
func place(deployable: Deployable, position: Vector2) -> bool:
	var snapped_pos: Vector2 = position.snapped(Vector2(grid_size, grid_size))
	
	if can_place(deployable, snapped_pos):
		budget_remaining -= deployable.cost
		placed_items.append({"deployable": deployable, "position": snapped_pos})
		
		item_placed.emit(deployable, snapped_pos)
		budget_changed.emit(budget_remaining)
		return true
		
	return false

## Removes a deployable at the given position and refunds cost.
func remove(position: Vector2) -> bool:
	var snapped_pos: Vector2 = position.snapped(Vector2(grid_size, grid_size))
	
	for i in range(placed_items.size()):
		if placed_items[i].position == snapped_pos:
			var item: Dictionary = placed_items[i]
			var deployable: Deployable = item.deployable
			
			budget_remaining += deployable.cost
			placed_items.remove_at(i)
			
			item_removed.emit(deployable, snapped_pos)
			budget_changed.emit(budget_remaining)
			return true
			
	return false
