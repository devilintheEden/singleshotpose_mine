- Three type of structure in a block

  - Corridor: can pass through two direction on the same height level
    - format: Corridor(is_relative, position, direction, level)
      - is_relative: is position relative to block (True) / is it global (False)
      - position: (vertical, horizontal)
      - direction: ("w","e")
      - level: floor level (base floor is 0)
  - Stair: a stair connecting different height level
    - format: Stair(is_relative, position, direction, level)
      - is_relative: is position relative to block (True) / is it global (False)
      - position: (vertical, horizontal)
      - direction: "e""w"n""s" for the direction of the higher side
      - level: floor level of the higher side

  - Platform: a platform that can connect to any adjacent tiles on the same height
    - format: Platform(is_relative, position, level)
      - is_relative: is position relative to block (True) / is it global (False)
      - position: (vertical, horizontal)
      - level: floor level (base floor is 0)

- Block:

  - format: Block(position, direction, platforms)
    - position: the global position of platform at (0,0) relative position
    - direction: the direction of the side with platforms (0,0) and (0,1)
    - platforms: an array containing all platforms in block

- ![A](E:\singleshotpose\puzzle_solver\images\A.jpg)
- block_A = Block((0,0), "n", [Platform(True, (0,0), 1), Platform(True, (0,1), 2), Corridor(True, (0,1), ("w", "e"), 1), Platform(True, (1,0), 1), Platform(True, (1,1), 1), Stair(True, (2,0), "e", 1), Corridor(True, (2,1), ("w", "e"), 0)])
- ![B](E:\singleshotpose\puzzle_solver\images\B.jpg)
- block_B = Block((0,0), "n", [Platform(True, (0,0), 2), Platform(True, (0,1), 2), Platform(True, (1,0), 2), Platform(True, (1,1), 1), Platform(True, (2,0), 1), Stair(True, (2,1), "n", 1)])
- ![C](E:\singleshotpose\puzzle_solver\images\C.jpg)
- block_C = Block((0,0), "n", [Platform(True, (0,0), 1), Platform(True, (0,1), 1), Platform(True, (1,0), 2), Platform(True, (1,1), 1), Platform(True, (2,0), 2), Stair(True, (2,1), "w", 2)])
- ![D](E:\singleshotpose\puzzle_solver\images\D.jpg)
- block_D = Block((0,0), "n", [Platform(True, (0,0), 1), Stair(True, (0,1), "s", 2), Stair(True, (0,2), "n", 1), Platform(True, (1,0), 1), Platform(True, (1,1), 2), Corridor(True, (1,2), ("n", "e"), 0)])
- ![E](E:\singleshotpose\puzzle_solver\images\E.jpg)
- block_E = Block((0,0), "n", [Platform(True, (0,0), 2), Platform(True, (0,1), 1), Stair(True, (1,0), "e", 1), Platform(True, (1,1), 1), Platform(True, (2,0), 1), Stair(True, (2,1), "s", 2)])
- ![F](E:\singleshotpose\puzzle_solver\images\F.jpg)
- block_tower = Block((0,0), "n", [Platform(True, (0,0), 2), Corridor(True, (0,0), ("w", "e"), 1), Platform(True, (0,1), 1), Stair(True, (1,0), "s", 3), Platform(True, (1,1), 3), Platform(True, (2,0), 3), Platform(True, (2,1), 3)])

