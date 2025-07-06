# Simple Hello R API Server using RestRserve
library(RestRserve)
library(jsonlite)

# Create application
app <- Application$new()

# Health check endpoint
app$add_get(
  path = "/health",
  FUN = function(request, response) {
    response$set_content_type("application/json")
    response$set_body(toJSON(list(
      status = "healthy",
      service = "Hello R API",
      version = "1.0.0"
    ), auto_unbox = TRUE))
  }
)

# Hello endpoint
app$add_post(
  path = "/api/hello",
  FUN = function(request, response) {
    tryCatch(
      {
        # Debug logging
        cat("Request received at /api/hello\n")
        cat("Request method:", request$method, "\n")
        cat("Content-Type:", request$get_header("Content-Type"), "\n")

        # Parse request body
        # RestRserve should parse JSON automatically when Content-Type is application/json
        # But it seems to wrap the body in a list structure
        name <- "World" # Default value
        
        # Debug: Check what we actually receive
        cat("request$body structure:\n")
        cat("  Class:", class(request$body), "\n")
        if (is.list(request$body)) {
          cat("  Names:", paste(names(request$body), collapse=", "), "\n")
          cat("  Length:", length(request$body), "\n")
        }
        
        # Try to access the parsed JSON data
        if (!is.null(request$body)) {
          # If body is already parsed as a list with name element
          if (is.list(request$body) && !is.null(request$body$name)) {
            name <- request$body$name
          }
          # If body is wrapped in another structure
          else if (is.list(request$body) && length(request$body) > 0) {
            # Check if it's the first element
            if (!is.null(request$body[[1]]) && is.list(request$body[[1]]) && !is.null(request$body[[1]]$name)) {
              name <- request$body[[1]]$name
            }
          }
        }

        # Create greeting
        greeting <- paste("Hello", name, "from R!")

        # Print to R console
        cat(greeting, "\n")

        # Return response
        response$set_content_type("application/json")
        response$set_body(toJSON(list(
          success = TRUE,
          message = greeting,
          timestamp = as.character(Sys.time()),
          r_version = R.version.string
        ), auto_unbox = TRUE))
      },
      error = function(e) {
        cat("Error in /api/hello:", e$message, "\n")
        response$set_status_code(500)
        response$set_content_type("application/json")
        response$set_body(toJSON(list(
          success = FALSE,
          error = e$message
        ), auto_unbox = TRUE))
      }
    )
  }
)

# Addition endpoint
app$add_post(
  path = "/api/add",
  FUN = function(request, response) {
    tryCatch(
      {
        # Debug logging
        cat("Request received at /api/add\n")
        
        # Parse request body
        a <- 0
        b <- 0
        
        # Debug: Check what we actually receive
        cat("request$body structure:\n")
        cat("  Class:", class(request$body), "\n")
        if (is.list(request$body)) {
          cat("  Names:", paste(names(request$body), collapse=", "), "\n")
          cat("  Length:", length(request$body), "\n")
        }
        
        # Try to access the parsed JSON data
        if (!is.null(request$body)) {
          # If body is already parsed as a list with a and b elements
          if (is.list(request$body)) {
            if (!is.null(request$body$a)) {
              a <- as.numeric(request$body$a)
            }
            if (!is.null(request$body$b)) {
              b <- as.numeric(request$body$b)
            }
          }
          # If body is wrapped in another structure
          else if (is.list(request$body) && length(request$body) > 0) {
            # Check if it's the first element
            if (!is.null(request$body[[1]]) && is.list(request$body[[1]])) {
              if (!is.null(request$body[[1]]$a)) {
                a <- as.numeric(request$body[[1]]$a)
              }
              if (!is.null(request$body[[1]]$b)) {
                b <- as.numeric(request$body[[1]]$b)
              }
            }
          }
        }
        
        # Calculate sum
        result <- a + b
        
        # Print to R console
        cat(sprintf("Addition: %g + %g = %g\n", a, b, result))
        
        # Return response
        response$set_content_type("application/json")
        response$set_body(toJSON(list(
          success = TRUE,
          a = a,
          b = b,
          result = result,
          operation = "addition",
          timestamp = as.character(Sys.time())
        ), auto_unbox = TRUE))
      },
      error = function(e) {
        cat("Error in /api/add:", e$message, "\n")
        response$set_status_code(500)
        response$set_content_type("application/json")
        response$set_body(toJSON(list(
          success = FALSE,
          error = e$message
        ), auto_unbox = TRUE))
      }
    )
  }
)

# Create backend
backend <- BackendRserve$new()

# Start server
cat("Starting Hello R API server on port 8081...\n")
backend$start(app, http_port = 8081)