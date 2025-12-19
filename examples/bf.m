instructions = ["+", "+", ">", "+", "+", "+", "+", "+", "[", "<", "+", ">", "-", "]",  "+", "+", "+", "+", "+", "+", "+", "+", "[", "<", "+", "+", "+", "+", "+", "+", ">", "-", "]", "<", "."];

data = zeros(1000, 1);
data_pointer = 0;

instruction_pointer = 0;
while (instruction_pointer < 35) {
	op = instructions[instruction_pointer];
	if (op == ">") {
		data_pointer += 1;
	}
	else if (op == "<") {
		data_pointer -= 1;
	}
	else if (op == "+") {
		data[data_pointer,0] += 1;
	}
	else if (op == "-") {
		data[data_pointer,0] -= 1;
	}
	else if (op == ".") {
		print data[data_pointer,0];
	}
	else if (op == "[") {
		if (data[data_pointer,0] == 0) {
			closing_pointer = instruction_pointer + 1;
			other_openings = 0;
			while (1 == 1) {
				if (instructions[closing_pointer] == "[") {
					other_openings += 1;
				}
				if (instructions[closing_pointer] == "]") {
					other_openings -= 1;
					if (other_openings == -1) {
						break;
					}
				}
				closing_pointer += 1;
			}
			instruction_pointer = closing_pointer;
		}
	}
	else if (op == "]") {
		if (data[data_pointer,0] != 0) {
			closing_pointer = instruction_pointer - 1;
			other_openings = 0;
			while (1 == 1) {
				if (instructions[closing_pointer] == "]") {
					other_openings += 1;
				}
				if (instructions[closing_pointer] == "[") {
					other_openings -= 1;
					if (other_openings == -1) {
						break;
					}
				}
				closing_pointer -= 1;
			}
			instruction_pointer = closing_pointer;
		}
	}
	instruction_pointer += 1;
}
