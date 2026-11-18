NAME = course-io-test
SRCS = main.c
ifeq ($(KEY_TEST),1)
NAME = course-key-test
SRCS = keyboard.c
endif
ifneq ($(filter %-npc,$(ARCH)),)
CFLAGS += -DCOURSE_NPC
endif
include $(AM_HOME)/Makefile
