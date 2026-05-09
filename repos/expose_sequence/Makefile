CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Iinclude

# Collect all component source files
SOURCES  := $(shell find . -path './.knowledge' -prune -o -name '*.cpp' -print)
OBJECTS  := $(SOURCES:.cpp=.o)

.PHONY: all clean

all: $(OBJECTS)
	@echo "Build complete for $(CURDIR)"

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	find . -name '*.o' -delete
	@echo "Clean complete"
