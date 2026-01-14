package com.ecole42.service.command;

public interface UserCommand<I, O> {
    O execute(I input);
}
