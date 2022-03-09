command_definitions = list()
available_help_commands = list()
with open('src/bot.py') as f:
    lines = f.readlines()
    for line_number in range(len(lines)):
        if 'client.command' in lines[line_number]:
            command = lines[line_number+1].strip().split(' ', 2)[-1]
            command = command[:command.find('(')]
            command_definitions.append(command)
        if '\'`pes.' in lines[line_number] or '"`pes.' in lines[line_number]:
            command = lines[line_number].strip().split(':')[0][6:-2]
            available_help_commands.append(command)

# print('\n'.join(command_definitions))
# print('\n'.join(available_help_commands))

missing_help_commands = set(command_definitions) - set(available_help_commands)
print('\n'.join(missing_help_commands))