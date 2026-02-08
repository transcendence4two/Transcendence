package emails.service.transcendence

import io.github.cdimascio.dotenv.dotenv
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class TranscendenceApplication

fun main(args: Array<String>) {
	val dotenv = dotenv {
		directory = "../../"
		ignoreIfMissing = true
	}
	dotenv.entries().forEach { (key, value) ->
		if (System.getenv(key) == null) {
			System.setProperty(key, value)
		}
	}

	runApplication<TranscendenceApplication>(*args)
}
