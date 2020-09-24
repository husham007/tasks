import logging
import os
import sys
import threading

from schedular import CronTab, EveryEvent
from xkcdapi import XkcdAPi

log = logging.getLogger('XKCD_SERVICE')
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(levelname)-10s %(name)-10s %(asctime)s %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(log_format)
log.addHandler(ch)

IMG_DIR = "xkcd_images"
MAX_SAVED_IMG = 2


class XkcdService:
    def __init__(self, hours=0, minutes=1):

        self._init_properties()
        self._hours = hours
        self._minutes = minutes
        self._scheduler = CronTab()
        self._create_event_and_start_scheduler()
        self._make_directory()
        self._delete_file_event = threading.Event()
        self._start_file_deleting_thread()

    def _init_properties(self):
        self._scheduler = None
        self._event = None
        self._comic_number = None
        self._delete_file_event = None

    def terminate(self, join=True):
        log.info('Started Terminating Process')
        self._remove_event(self._event)
        self._scheduler.terminate(join)
        self._delete_file_event.set()
        self._init_properties()

    def _create_event(self, action, minutes=0, hours=0, days=0, enabled=True, threaded=False):
        return EveryEvent(action, ev_minutes=minutes, ev_hours=hours, ev_days=days, threaded=threaded, enabled=enabled)

    def _add_event(self, *event):
        self._scheduler.add_events(event)

    def _remove_event(self, *event):
        self._scheduler.remove_events(event)

    def _event_job(self):
        log.info('i am the Scheduled Job')
        try:
            while True:
                number = XkcdAPi.get_random_comic_number()
                if self._comic_number != number:
                    self._comic_number = number
                    break

            img_content, img_title = XkcdAPi.get_image(number)
            if img_title:
                self._create_file(img_content, img_title)

        except Exception as e:
            log.error(e)

    def _create_file(self, content, title):
        log.info('Creating file with name %s' % title)
        path = os.path.join(self._get_img_dir_path, title + '.png')
        with open(path, "wb") as file:
            try:
                file.write(content)
                self._delete_file_event.set()
            except Exception as e:
                log.error(e)

    def _delete_file_thread(self):
        while True:
            log.info(' i am delete file thread and waiting ...')

            if self._delete_file_event:
                self._delete_file_event.wait()

            if not self._scheduler or not self._delete_file_event:
                return

            no_of_img = self._no_of_img_in_dir()
            log.info('No. of files in img dir:%i' % no_of_img)

            if no_of_img > MAX_SAVED_IMG:
                self._get_oldest_file_and_delete()

            if self._delete_file_event:
                self._delete_file_event.clear()

            log.info('Wait is Over')

    def _get_oldest_file_and_delete(self):
        img = min([os.path.join(self._get_img_dir_path, d) for d in os.listdir(self._get_img_dir_path)], key=os.path.getmtime)
        try:
            os.remove(img)
            log.info('File: %s ,deleted!!!' % img)
            #self.terminate()
        except OSError as e:
            log.error(e)


    def _no_of_img_in_dir(self):
        return len(os.listdir(self._get_img_dir_path))

    def _make_directory(self):
        path = self._get_img_dir_path
        try:
            os.makedirs(path, exist_ok=True)
            log.info('Image Directory Created...')

        except OSError as error:
            print(error)

    @property
    def _get_img_dir_path(self):
        return os.path.join(os.getcwd(), IMG_DIR)

    def _create_event_and_start_scheduler(self):
        self._event = self._create_event(self._event_job, hours=self._hours, minutes=self._minutes, threaded=True, enabled=True)
        self._event.enabled = True
        self._scheduler.add_events(self._event)

        try:
            self._scheduler.start()
            '''
            while True:
                time.sleep(0.5)
                if not self._scheduler:
                    break
            '''
        except (KeyboardInterrupt, SystemExit):
            pass

    def _start_file_deleting_thread(self):
        log.info('Delete file thread created and Started')
        thread = threading.Thread(target=self._delete_file_thread)
        thread.start()


service = XkcdService()
