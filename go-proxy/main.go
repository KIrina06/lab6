package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gorilla/mux"
)

const (
	BackendHost = "http://localhost:8000"
	UpdateURLFmt = "/api/private/requests/%s/update_request/"
)

type updateHandler struct {
	client *http.Client
	delay time.Duration
	token string
}

type updateRequest struct {
	RequestStatus int `json:"req_status"`
}

func main() {
	token := "my-super-secret-token"
	if len(os.Args) == 2 {
		token = os.Args[1]
		fmt.Printf("Got custom token: %s\n", token)
	} else {
		fmt.Printf("Using default token: %s\n", token)
	}

	r := mux.NewRouter()
	handler := newUpdateHanlder(token)
	r.Handle("/api/request/{id:[0-9]+}/status/{status:[0-9]+}", handler)

	fmt.Println("Listening on :3333")
	srv := &http.Server{
		Addr: ":3333",
		Handler: r,
		
	}
	fmt.Println(srv.ListenAndServe())
}

func newUpdateHanlder(token string) *updateHandler {
	return &updateHandler{
		client: &http.Client{Timeout: 1 * time.Second},
		delay: 7 * time.Second,
		token: token,
	}
}

func (h *updateHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	requestId := vars["id"]
	status := vars["status"]
	fmt.Printf("Update request %s: status %s in %s\n", requestId, status, h.delay)

	// already validated via gorilla/mux
	statusInt, _ := strconv.ParseInt(status, 10, 64)

	select {
	case <- time.After(h.delay):
	case <- r.Context().Done():
		msg := "request cancelled"
		w.WriteHeader(400)
		w.Write([]byte(msg))
		fmt.Println(msg)
		return
	}

	data := updateRequest{RequestStatus: int(statusInt)}
	jsonData, _ := json.Marshal(data)
	url := BackendHost + fmt.Sprintf(UpdateURLFmt, requestId)
	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
	if err != nil {
		msg := fmt.Sprintf("create request: %s", err.Error())
		w.WriteHeader(500)
		w.Write([]byte(msg))
		fmt.Println(msg)
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Token", h.token)

	res, err := h.client.Do(req)
	if err != nil {
		msg := fmt.Sprintf("send request: %s", err.Error())
		w.WriteHeader(500)
		w.Write([]byte(msg))
		fmt.Println(msg)
		return
	}
	defer res.Body.Close()

	response, err := io.ReadAll(res.Body)
	if err != nil {
		msg := fmt.Sprintf("read response body: %s", err.Error())
		w.WriteHeader(500)
		w.Write([]byte(msg))
		fmt.Println(msg)
		return
	}

	w.WriteHeader(res.StatusCode)
	w.Write(response)
}
