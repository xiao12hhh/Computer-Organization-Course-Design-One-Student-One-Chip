BUILD := ../build/pa1
.PHONY: test setup count
count:
	python3 count.py
test:
	mkdir -p $(BUILD)
	cc -std=c11 -Wall -Wextra -Werror -g -fsanitize=address,undefined expr.c test_expr.c -o $(BUILD)/test_expr
	$(BUILD)/test_expr
	python3 test_random.py
setup:
	bash setup.sh
