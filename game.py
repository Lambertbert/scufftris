from grid import Grid 
from blocks import *  # Importing different tetromino (block) shapes
from settings import *
from colors import Colors
import random, sys
from menu import Menus


class Game:
    def __init__(self):
        # Initializes the game with an empty grid, block queue, and starting block
        self.grid = Grid()
        # List of all block shapes (tetrominoes)
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()  # The block currently falling
        self.next_block = self.get_random_block()  # The block to appear after the current one
        self.game_over = False  # A flag to track if the game is over
        self.score = 0  # Keeps track of the player's score
        
        # Load sounds for rotating blocks and clearing rows
        self.rotate_sound = pygame.mixer.Sound("Sounds/rotate.wav")
        self.clear_sound = pygame.mixer.Sound("Sounds/clear.ogg")
        self.hard_drop_sound = pygame.mixer.Sound("Sounds/harddrop.mp3")
    
        # Load and play background music on loop
        pygame.mixer.music.load("Sounds/music.ogg")
        pygame.mixer.music.play(-1)  # -1 means the music loops indefinitely
        pygame.mixer.music.set_volume(0.3) # Set the volume of the background music
        
    def play(self, screen):
        # Main game loop (runs continuously)
        clock = pygame.time.Clock()
        self.paused = False # Flag to track if the game is paused
        speed = 300
        last_click_time = 0
        click_delay = 300
        # Custom user event for updating the game every few milliseconds
        GAME_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(GAME_UPDATE, speed) # Set the event to trigger every `speed` milliseconds
        # Initialize timers for controlling movement (left, right, down)
        move_left_timer, move_right_timer, move_down_timer = 0, 0, 0
        move_delay = 200 # Delay (in milliseconds) to prevent continuous movement when holding keys
        # down_move_delay = 1500
        
        while True:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if not self.paused and not self.game_over:
                        if event.key == controls['hard_drop']:
                            self.hard_drop()
                        if event.key == controls['rotate']:
                            self.rotate()
                    if self.game_over == True:  # Reset the game if it's over
                            self.game_over = False
                            self.reset()
                            
                if event.type == GAME_UPDATE and not self.paused and not self.game_over:
                    self.move_down()

            if not self.paused and not self.game_over:
                keys = pygame.key.get_pressed()
                if (keys[controls['left']]) and current_time - move_left_timer > move_delay:
                    # print(current_time , move_left_timer , move_delay)
                    self.move_left()
                    move_left_timer = current_time
                if (keys[controls['right']]) and current_time - move_right_timer > move_delay:
                    # print(current_time , move_right_timer , move_delay)
                    self.move_right()
                    move_right_timer = current_time
                if (keys[controls['down']]) and current_time - move_down_timer > move_delay:
                    # print(current_time , move_down_timer , move_delay)
                    self.move_down()
                    move_down_timer = current_time
                    self.update_score(0, 1)

            # Draw game state
            screen.fill(Colors.dark_blue)
            self.draw(screen)
            
            if self.paused:
                # pygame.display.update()  # Update the display to show the pause menu
                        # Event handling for the pause menu
                 # Handle mouse input for the pause menu
                resume_rect, quit_rect, increase_speed_rect, decrease_speed_rect, increase_move_rect, decrease_move_rect, back_to_menu_rect = Menus().pause_menu(screen,speed,move_delay)
                mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
                mouse_click = pygame.mouse.get_pressed()  # Get the state of mouse buttons
                
                # Handle mouse clicks with a debounce delay
                if mouse_click[0] and current_time - last_click_time > click_delay:  # Left-click
                    last_click_time = current_time
                    if resume_rect.collidepoint(mouse_pos):  # Resume button clicked
                        self.paused = not self.paused
                    elif quit_rect.collidepoint(mouse_pos):  # Quit button clicked
                        pygame.quit()
                        sys.exit()
                    elif back_to_menu_rect.collidepoint(mouse_pos):  # return button clicked
                        print(self.paused,self.game_over)
                        Menus().main_menu(screen, DISPLAY_WIDTH, DISPLAY_HEIGHT)
                        self.paused = not self.paused
                        self.reset()
                    elif increase_speed_rect.collidepoint(mouse_pos):  # Increase speed clicked
                        if speed > 50:  # Limit the speed increase
                            speed -= 50
                            pygame.time.set_timer(GAME_UPDATE, speed)  # Update the game speed
                    elif decrease_speed_rect.collidepoint(mouse_pos):  # Decrease speed clicked
                        if speed < 1000:  # Limit the speed decrease
                            speed += 50
                            pygame.time.set_timer(GAME_UPDATE, speed)  # Update the game speed
                    elif increase_move_rect.collidepoint(mouse_pos):  # Increase move clicked
                        if move_delay > 0:  # Limit the move increase
                            move_delay -= 50
                            pygame.time.set_timer(GAME_UPDATE, speed)  # Update the move speed
                    elif decrease_move_rect.collidepoint(mouse_pos):  # Decrease speed clicked
                        if move_delay < 1000:  # Limit the move decrease
                            move_delay += 50
                            pygame.time.set_timer(GAME_UPDATE, speed)  # Update the move speed

            # Blit game_screen onto the main screen
            main_screen = pygame.display.get_surface()
            main_screen.blit(screen, (0, 0))

            pygame.display.update()
            clock.tick(FPS)
    
    def update_score(self, lines_cleared, move_down_points):
        # Updates the score based on the number of lines cleared and points for moving blocks down
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        self.score += move_down_points  # Add points for moving blocks down

    def get_random_block(self):
        # Selects a random block from the block list, ensuring no duplicates
        if len(self.blocks) == 0:  # Reset the list if all blocks have been used
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)  # Choose a random block
        self.blocks.remove(block)  # Remove it from the list to avoid immediate repetition
        return block

    def move_left(self):
        # Moves the current block left and checks if it remains inside and fits
        self.current_block.move(0, -1)
        if self.block_inside(self.current_block) == False or self.block_fits(self.current_block) == False:
            self.current_block.move(0, 1)  # Undo the move if invalid

    def move_right(self):
        # Moves the current block right and checks if it remains inside and fits
        self.current_block.move(0, 1)
        if self.block_inside(self.current_block) == False or self.block_fits(self.current_block) == False:
            self.current_block.move(0, -1)  # Undo the move if invalid

    def move_down(self):
        # Moves the current block down and locks it if it can't move further
        self.current_block.move(1, 0)
        if self.block_inside(self.current_block) == False or self.block_fits(self.current_block) == False:
            self.current_block.move(-1, 0)  # Undo the move if invalid
            self.lock_block()  # Lock the block in place if it can't move down further
            
    def hard_drop(self):
        # Moves the block instantly to the lowest possible position
        while self.block_inside and self.block_fits(self.current_block):
            self.current_block.move(1, 0)
        self.current_block.move(-1, 0)
        self.hard_drop_sound.play()
        self.lock_block()

    def lock_block(self):
        # Locks the current block in the grid and prepares the next block
        tiles = self.current_block.get_cell_positions()  # Get the block's current positions
        for position in tiles:
            # Set the block's id in the grid to lock its position
            self.grid.grid[position.row][position.column] = self.current_block.id
        self.current_block = self.next_block  # Move to the next block
        self.next_block = self.get_random_block()  # Prepare a new block
        rows_cleared = self.grid.clear_full_rows()  # Check if any rows were completed
        if rows_cleared > 0:
            self.clear_sound.play()  # Play sound if rows were cleared
            self.update_score(rows_cleared, 0)  # Update score based on cleared rows
        if self.block_fits(self.current_block) == False:
            self.game_over = True  # End the game if a new block can't fit

    def reset(self):
        # Resets the game to the initial state (empty grid, new blocks, reset score)
        self.grid.reset()  # Reset the grid
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]  # Reset block list
        self.current_block = self.get_random_block()  # Start with a new block
        self.next_block = self.get_random_block()  # Prepare the next block
        self.score = 0  # Reset score

    def block_fits(self, block):
        # Checks if the current block fits in its current position
        tiles = block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:  # Check if tile is in an empty cell
                return False
        return True

    def rotate(self):
        # Rotates the current block and checks if it fits
        self.current_block.rotate()
        if self.block_inside(self.current_block) == False or self.block_fits(self.current_block) == False:
            self.current_block.undo_rotation()  # Undo the rotation if it doesn't fit
        else:
            self.rotate_sound.play()  # Play the rotate sound if the rotation was successful

    def block_inside(self, block):
        # Checks if the current block is completely within the grid boundaries
        tiles = block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.column) == False:  # Check if the tile is inside the grid
                return False
        return True
    
    def get_shadow_block(self):
        # Create a shadow block to preview where the block will land
        shadow_block = self.current_block.clone()
        while self.block_inside(shadow_block) and self.block_fits(shadow_block):
            shadow_block.move(1, 0) # Shadow block is placed at the bottom
        shadow_block.move(-1, 0) # Place shadow block 1 row up if it does not fit
        return shadow_block

    def draw(self, screen):
        # Draws the grid and the current and next blocks on the screen
        self.grid.draw(screen)  # Draw the grid
        
        self.get_shadow_block().draw(screen, 11, 11, shadow=True)  # Draw a shadow block on the grid
        self.current_block.draw(screen, 11, 11)  # Draw the current block on the grid

        # Draw the next block in a preview box (with slight adjustment for size)
        if self.next_block.id == 3:  # For OBlock, adjust the position slightly
            self.next_block.draw(screen, 255, 290)
        elif self.next_block.id == 4:  # For TBlock, adjust the position slightly
            self.next_block.draw(screen, 255, 280)
        else:
            self.next_block.draw(screen, 270, 270)  # For all other blocks