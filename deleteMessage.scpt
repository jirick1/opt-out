-- AppleScript to delete messages containing "STOP" in the Messages app

tell application "Messages" to activate
delay 1

tell application "System Events"
    tell process "Messages"
        set frontmost to true
        delay 1

        -- Access the conversations list
        tell window 1
            set convList to outline 1 of scroll area 1 of splitter group 1
            set convCount to count of rows of convList

            -- Loop through each conversation
            repeat with i from 1 to convCount
                set convRow to row i of convList
                select convRow
                delay 0.5

                -- Access the messages in the conversation
                set messageList to scroll area 2 of splitter group 1
                set messageItems to every UI element of messageList

                -- Loop through messages from last to first
                repeat with j from (count of messageItems) to 1 by -1
                    set messageItem to item j of messageItems

                    try
                        -- Check if the message contains "STOP"
                        if exists static text 1 of messageItem then
                            set messageText to value of static text 1 of messageItem
                            if messageText is equal to "STOP" then
                                -- Right-click (Control-click) on the message
                                perform action "AXShowMenu" of messageItem
                                delay 0.5
                                -- Click "Delete" from the context menu
                                click menu item "Delete" of menu 1 of messageItem
                                delay 0.5
                                -- Confirm deletion if prompted
                                if exists button "Delete" of window 1 then
                                    click button "Delete" of window 1
                                else if exists button "Delete" of sheet 1 of window 1 then
                                    click button "Delete" of sheet 1 of window 1
                                end if
                                delay 0.5
                            end if
                        end if
                    end try
                end repeat
            end repeat
        end tell
    end tell
end tell
